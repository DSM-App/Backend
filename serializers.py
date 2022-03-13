from rest_framework import serializers
from groups.serializers import GroupSerializer, GroupMembersSerializer
from .models import OwnershipCopyRights, Vote
from Decentralized_social_media.settings import FRONTEND_URL


class OwnershipCopyRightsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OwnershipCopyRights
        fields = [
            "id",
            "copyrighted_by",
            "reason",
            "number_of_copyrighted_votes",
            "number_of_not_copyrighted_votes",
            "closed",
            "created_on",
            "group",
        ]

        read_only_fields = [
            "id",
            "copyrighted_by",
            "group",
        ]

    def create(self, validated_data):
        print("context = ", self.context)
        print("validated_Data = ", validated_data)
        return OwnershipCopyRights.objects.create(
            copyrighted_by=self.context["copyrighted_by"],
            reason=validated_data["reason"],
            group=self.context["group"],
            blogpost=self.context["blogpost"],
            carousel=self.context["carousel"],
        )


class OwnershipCopyRightsDetailsSerializer(serializers.ModelSerializer):

    copyrighted_by = GroupMembersSerializer()
    group = GroupSerializer()

    created_on = serializers.SerializerMethodField()

    def get_created_on(self, copyright):
        return copyright.created_on.timestamp()

    post_info = serializers.SerializerMethodField()

    def get_post_info(self, copyright):
        if copyright.blogpost:
            return f"{FRONTEND_URL}/blogpost/{copyright.blogpost.slug}"
        else:
            return f"{FRONTEND_URL}/carousel/{copyright.carousel.slug}"

    class Meta:
        model = OwnershipCopyRights
        fields = [
            "id",
            "copyrighted_by",
            "reason",
            "number_of_copyrighted_votes",
            "number_of_not_copyrighted_votes",
            "post_info",
            "created_on",
            "group",
        ]


class VoteDetailsSerializer(serializers.ModelSerializer):

    author = GroupMembersSerializer()

    created_on = serializers.SerializerMethodField()

    def get_created_on(self, copyright):
        return copyright.created_on.timestamp()

    class Meta:
        model = Vote
        fields = ["id", "author", "created_on", "comment"]
