from rest_framework import serializers
from .models import Profile
from django.contrib.auth import get_user_model

# from utils import create_email_update_token


User = get_user_model()


# Send Basic Profile Data
class UserNameSerializer(serializers.ModelSerializer):
    """
    We only want to send username for basic profile data along with other profile attributes
    """

    class Meta:
        model = User
        fields = ["username"]


class ProfileSerializer(serializers.ModelSerializer):

    user = UserNameSerializer()

    class Meta:
        model = Profile
        fields = [
            "profile_pic",
            "first_name",
            "last_name",
            "user",
            "bio",
            "number_of_followers",
            "number_of_followings",
        ]

    # We are not sending id of the profile or user to prevent reverse mapping of user ID's to usernames
    # As user ID's are sent in JWT

    def update(self, instance, validated_data):
        """
        Only non dangerous fields are updated here, as dangerous fields like user, email require their own validation
        """

        instance.first_name = validated_data["first_name"]
        instance.last_name = validated_data["last_name"]
        instance.bio = validated_data["bio"]
        instance.save()
        return instance


class ProfileDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "user__username",
            "profile_pic",
            "first_name",
            "last_name",
            "number_of_followers",
            "number_of_followings",
            "bio",
        ]


# Update Profile picture - Profile picture is handled separately
class ProfilePicUpdateSerializer(serializers.ModelSerializer):
    """
    Separate endpoint for updating profile picture because submitting profile picture
    in a form along with other fields is not a good UX
    """

    class Meta:
        model = Profile
        fields = ["profile_pic"]

    def update(self, instance, validated_data):
        print(f"instance = {instance} \n validated data = {validated_data} ")
        instance.profile_pic = validated_data["profile_pic"]
        instance.save()
        return instance


class UsernameUpdateSerializer(serializers.ModelSerializer):
    """
    An endpoint to update username. Since it requires it's own validation.
    it can be placed in non-dangerous fields with validation. But if there is any error in
    username other fields also won't be saved which is not a good UX
    """

    class Meta:
        model = User
        fields = ["username"]

    def validate_username(self, username):
        if (
            (username and User.objects.filter(username=username))
            .exclude(is_active=False)
            .exists()
        ):
            raise serializers.ValidationError("Username already taken")
        return username

    def update(self, instance, validated_data):
        """
        Updates the username
        """

        instance.username = validated_data["username"]
        instance.save()
        return instance


# Sends all confidential data llke email, can be only accessed by profile owner
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]


class ProfileDetailSerializer(serializers.ModelSerializer):

    user = UserDetailSerializer()

    class Meta:
        model = Profile
        fields = [
            "profile_pic",
            "first_name",
            "last_name",
            "user",
            "bio",
            "number_of_followers",
            "number_of_followings",
        ]
