from UserProfile.utils import create_email_update_token
from functools import partial
from rest_framework import generics, permissions, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Profile, EmailUpdateToken
from rest_framework import status
from .serializers import (
    ProfileSerializer,
    ProfilePicUpdateSerializer,
    UsernameUpdateSerializer,
    ProfileDetailSerializer,
)
from .permissions import ProfilePagePermissions, ReadOnly
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.parsers import MultiPartParser, FormParser


User = get_user_model()


class ProfilePage(APIView):
    """
    Request parameters = {first_name, last_name, bio} for PUT , authentication required
                         No params for GET, no authentication required
    """

    # Anyone can perform the GET request but only authenticated owner can perform PUT, POST and DELETE

    permission_classes = [
        ReadOnly | (permissions.IsAuthenticated & ProfilePagePermissions)
    ]

    def get_profile_by_username(self, username):
        try:
            profile = Profile.objects.get(user__username=username)
            return profile
        except Exception as e:
            return None

    def get_profile_by_id(self, request, id):
        try:
            profile = Profile.objects.get(user__id=id)
            self.check_object_permissions(request, profile)
            return profile
        except Exception as e:
            return None

    def get(self, request, username):
        print("Got the request ")
        profile = self.get_profile_by_username(username)
        if not profile:
            return Response("Profile not found", status=status.HTTP_400_BAD_REQUEST)
        profile_serializer = ProfileSerializer(
            profile, context={"request": request}
        )  # Serializing data to return JSON
        return Response(profile_serializer.data, status=status.HTTP_200_OK)

    def put(self, request, username):
        profile = self.get_profile_by_id(request, request.user.id)
        profile_update_serializer = ProfileSerializer(
            profile, data=request.data, partial=True
        )
        if profile_update_serializer.is_valid():
            profile_update_serializer.save()
            return Response(profile_update_serializer.data)
        return Response(
            profile_update_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class ProfilePictureUpload(APIView):
    """
    Endpoint to update Profile picture

    Request parameters: {profile_pic: image file} (send through form data in postman) for PUT, request must be authenticated
    """

    parser_classes = (
        MultiPartParser,
        FormParser,
    )
    permission_classes = [permissions.AllowAny]
    # authentication_classes = []
    # permission_classes = [(permissions.IsAuthenticated & ProfilePagePermissions)]

    def put(self, request, format=None):
        print(f"{request.META['CONTENT_TYPE']}")
        print(f"request.data = {request.data}, ")
        print(f"request.FILES = {dir(request.FILES.items())}")
        try:
            profile = Profile.objects.get(user__id=request.user.id)
            self.check_object_permissions(request, profile)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

        profile_pic_serializer = ProfilePicUpdateSerializer(profile, data=request.data)
        if profile_pic_serializer.is_valid():
            profile_pic_serializer.save()
            return Response(profile_pic_serializer.data, status=status.HTTP_200_OK)
        return Response(
            profile_pic_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class ChangeEmailRequest(APIView):
    """
    An endpoint to update new email
    It takes the request and sends OTP

    Request parameters: {new_email} PUT authenticated
    """

    permission_classes = [(permissions.IsAuthenticated & ProfilePagePermissions)]

    def put(self, request):

        try:
            user = User.objects.get(id=request.user.id)
            new_email = request.data["new_email"]
        except Exception as e:
            return Response("New Email cannot be empty", status.HTTP_400_BAD_REQUEST)

        if user.email == new_email:
            return Response(
                "New Email cannot be same as old email",
                status=status.HTTP_403_FORBIDDEN,
            )

        create_email_update_token(user, new_email)
        return Response(status=status.HTTP_200_OK)


class ChangeEmailVerify(APIView):
    """
    An endpoint to receive OTP sent for updating new email

    Request parameters: {token (OTP sent),} PUT authenticated
    """

    permission_classes = [(permissions.IsAuthenticated & ProfilePagePermissions)]

    def put(self, request):
        token = request.data["token"]

        try:
            sent_token = EmailUpdateToken.objects.get(
                token=token, user__id=request.user.id
            )
        except Exception as e:
            return Response("Token not found", status=status.HTTP_400_BAD_REQUEST)

        if sent_token.token == token and timezone.now() <= sent_token.expires_at:
            sent_token.user.email = sent_token.new_email
            sent_token.user.save()
            sent_token.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ChangeUsername(APIView):
    """
    An endpoint to change username. It is handled separately from other fields as we
    need to check if the username is unique

    Request parameters: {new_username} PUT authenticated
    """

    permission_classes = [(permissions.IsAuthenticated & ProfilePagePermissions)]

    def put(self, request):
        try:
            new_username = request.data["new_username"]
            user = User.objects.get(id=request.user.id)

        except KeyError:
            return Response(
                "new_username should be present in request",
                status=status.HTTP_400_BAD_REQUEST,
            )

        except User.DoesNotExist:
            return Response("user does not exists", status=status.HTTP_404_NOT_FOUND)

        username_update_serializer = UsernameUpdateSerializer(
            user, data={"username": new_username}
        )
        if username_update_serializer.is_valid():
            username_update_serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(
            username_update_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class ProfileDetailView(APIView):
    """
    An endpoint which sends all details about profile including confidentail data like email.
    Only owner of the profile can make this

    Request parameters: None GET authenticated
    """

    permission_classes = [(permissions.IsAuthenticated & ProfilePagePermissions)]

    def get(self, request):

        try:
            profile = Profile.objects.get(user__id=request.user.id)
            self.check_object_permissions(request, profile)
        except Profile.DoesNotExist:
            return Response("profile does not exists", status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response(
                "You are not authorized to access this object",
                status=status.HTTP_400_BAD_REQUEST,
            )
        print(f"profile = {profile}")
        profile_detail_serializer = ProfileDetailSerializer(profile)
        return Response(profile_detail_serializer.data, status=status.HTTP_200_OK)
