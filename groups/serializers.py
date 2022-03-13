from rest_framework import serializers
from UserProfile.models import Profile
from django.contrib.auth import get_user_model

from groups.models import Group


User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """
    We only want to send username for basic profile data along with other profile attributes
    """

    class Meta:
        model = Profile
        fields = ["first_name", "last_name", "profile_pic"]


class GroupMembersSerializer(serializers.ModelSerializer):
    """
    Used when returning list of users with only required data (eg: in search fields, followers,..)
    """

    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ["id", "username", "profile"]


class GroupSerializer(serializers.ModelSerializer):
    """
    Serializes a group object
    """

    class Meta:
        model = Group
        fields = ["id", "name", "icon"]


class GroupDetailsSerializer(serializers.ModelSerializer):
    """
    Sends all details of a group
    """

    created_at = serializers.SerializerMethodField()

    def get_created_at(self, group):
        return group.created_at.timestamp()

    is_member = serializers.SerializerMethodField()

    def get_is_member(self, group):
        if "request" not in self.context or self.context["request"].user.is_anonymous:
            return False
        return self.context["request"].user in group.members.all()

    class Meta:
        model = Group
        fields = [
            "id",
            "name",
            "description",
            "icon",
            "banner",
            "number_of_people",
            "created_at",
            "is_member",
        ]
