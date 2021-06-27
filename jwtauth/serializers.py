# jwtauth/serializers.py

from datetime import timedelta
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .utils import send_verify_emai, password_check


User = get_user_model()

# Response format for for form request
# {
#    "error": False or True,
#    "success": False or True,
#    "field": field which caused the error (if any)   ,
#    "message": error message or success message
# }


class UserCreateSerializer(serializers.Serializer):

    """
    Serializer for user signup
    """

    username = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    password2 = serializers.CharField(
        style={"input_type": "password"}, write_only=True, label="Confirm password"
    )

    def validate_username(self, username):
        if (
            (username and User.objects.filter(username=username))
            .exclude(is_active=False)
            .exists()
        ):
            raise serializers.ValidationError("Username already taken")
        return username

    def validate_email(self, email):
        if email and User.objects.filter(email=email).exclude(is_active=False).exists():
            raise serializers.ValidationError("Email already taken")
        return email

    def validate_password(self, password):
        try:
            password_check(password)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return password

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("Passwords don't match")
        return data

    extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        username = validated_data["username"]
        email = validated_data["email"]
        password = validated_data["password"]
        password2 = validated_data["password2"]

        # Same user might have used same username and email but might have failed to
        # verify his / her email. So delete his previous entry only if it is inactive

        User.objects.filter(email=email).exclude(is_active=True).delete()
        User.objects.filter(username=username).exclude(is_active=True).delete()

        user = User.objects.create_user(
            username=username, email=email, password=password
        )

        send_verify_emai(user, email)

        user.save()

        return user


class ChangePasswordSerializer(serializers.Serializer):

    """
    Serializer for password change endpoint.
    """

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
