# jwtauth/views.py

from django.contrib.auth import get_user_model
from django.http.response import HttpResponse
from rest_framework import permissions
from rest_framework import response, decorators, permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import ChangePasswordSerializer, UserCreateSerializer
from django.contrib.auth import authenticate
from rest_framework import generics
from rest_framework.views import APIView
from .models import EmailVerificationTokens
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated


User = get_user_model()

# Register View
@decorators.api_view(["POST"])
@decorators.permission_classes([permissions.AllowAny])
def registration(request):
    serializer = UserCreateSerializer(data=request.data)
    print("HERE")
    if not serializer.is_valid():
        print("ERROS", serializer.errors)
        return response.Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    user = serializer.save()

    return response.Response(
        {"message": "You are successfully signed up"}, status.HTTP_201_CREATED
    )


# Login View
@decorators.api_view(["POST"])
@decorators.authentication_classes([])
@decorators.permission_classes([permissions.AllowAny])
def login(request):

    try:
        username = request.data["username"]
        user = User.objects.get(username=username)
    except Exception as e:
        return response.Response(
            {"username": "User doesn't exist"}, status.HTTP_400_BAD_REQUEST
        )

    try:
        password = request.data["password"]
        print(password)
    except:
        return response.Response(
            {"password": "Password not valid"}, status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)

    # If the login is successfull we will send username and profile pic it will be useful in frontend
    # for icons and generating profile url's

    if user is not None:
        profile_pic = None
        if user.profile.profile_pic:
            profile_pic = user.profile.profile_pic.url

        refresh = RefreshToken.for_user(user)
        res = {
            "message": "Logged in successfully",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "username": user.get_username(),
            "profile_pic": profile_pic,
        }
        return response.Response(res, status.HTTP_200_OK)
    else:
        return response.Response(
            {"password": "Password not valid"}, status=status.HTTP_400_BAD_REQUEST
        )


# Change Password
class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """

    serializer_class = ChangePasswordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return response.Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            resp = {
                "status": "success",
                "code": status.HTTP_200_OK,
                "message": "Password updated successfully",
                "data": [],
            }

            return response.Response(resp)

        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# verify email address
class VerifyEmailView(APIView):
    def post(self, request):
        token = request.data.get("token")
        email = request.data.get("email")
        print(f"token = {token} , email = {email}")
        try:
            sent_token = EmailVerificationTokens.objects.get(
                token=token, user__email=email
            )
        except Exception as e:
            return response.Response("Token Not found", status=400)

        # We need to check
        # 1. Expiry time
        # 2. Token Value
        # 3. Email

        print("current time ", timezone.now())
        print("Expires at ", sent_token.expires_at)

        if timezone.now() <= sent_token.expires_at:
            print("expiry verification passed")

        if token == sent_token.token:
            print("token verification passed")

        if sent_token.user.email == email:
            print("email verification passed")

        if (
            timezone.now() <= sent_token.expires_at
            and token == sent_token.token
            and sent_token.user.email == email
        ):
            sent_token.user.is_active = True
            sent_token.user.save()
            sent_token.delete()
            return response.Response("Email Verified succesfully", status=200)

        return response.Response("Token Verification Failed", status=400)


# Logout user
class LogoutView(APIView):

    # TODO: user should be logged in to logout, think about this.
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return response.Response("success", status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return response.Response(
                "refresh token not found", status=status.HTTP_400_BAD_REQUEST
            )
