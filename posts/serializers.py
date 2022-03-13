from rest_framework import serializers
from django.contrib.auth import get_user_model
from UserProfile.models import Profile
from .models import (
    BlogPost,
    BlogPostComment,
    PostImage,
    PostVideo,
    Carousel,
    CarouselComment,
)
import json
from groups.serializers import GroupSerializer
from groups.models import Group


class BlogPostSerializer(serializers.HyperlinkedModelSerializer):

    author = serializers.CharField(source="author.username", read_only=True)
    profile_pic_url = serializers.SerializerMethodField()

    # profile pic url, if doesn't exists send empty string
    def get_profile_pic_url(self, blog):
        if blog.author.profile.profile_pic:
            return blog.author.profile.profile_pic.url
        return ""

    # To tell if a person has liked or disliked this post earlier
    liked = serializers.SerializerMethodField()
    disliked = serializers.SerializerMethodField()

    def get_liked(self, blog):
        """
        Returns True if the person has liked the post, false if didn't like the post, None if anonymous
        """
        request = self.context.get("request")

        if request.user.is_anonymous:
            return None

        return request.user in blog.liked_people.all()

    def get_disliked(self, blog):
        """
        Returns True if the person has disliked the post, false if didn't dislike the post, None if anonymous
        """
        request = self.context.get("request")

        if request.user.is_anonymous:
            return None

        return request.user in blog.disliked_people.all()

    owner = serializers.SerializerMethodField()

    def get_owner(self, blogpost):
        if self.context["request"].user.is_anonymous:
            return None

        return self.context["request"].user == blogpost.author

    post_url = serializers.HyperlinkedIdentityField(
        view_name="blogpost-detail", lookup_field="slug", read_only=True
    )

    comments = serializers.SerializerMethodField()

    def get_comments(self, post):
        return post.comments.all().count()

    post_type = serializers.ReadOnlyField(default="blogpost")

    # We want to convert datetime objects to unix time
    published = serializers.SerializerMethodField()
    last_edited = serializers.SerializerMethodField()

    def get_published(self, post):
        return post.published.timestamp()

    def get_last_edited(self, post):
        return post.last_edited.timestamp()

    # we need to return group when deserializing
    group = serializers.CharField(source="group.name", read_only=True)

    class Meta:

        model = BlogPost

        fields = [
            "id",
            "title",
            "content",
            "published",
            "last_edited",
            "author",
            "owner",
            "post_url",
            "profile_pic_url",
            "post_url",
            "likes",
            "dislikes",
            "comments",
            "liked",
            "disliked",
            "slug",
            "post_type",
            "group",
        ]

        read_only_fields = [
            "id",
            "author",
            "profile_pic_url",
            "published",
            "last_edited",
            "post_url",
            "likes",
            "dislikes",
            "liked",
            "diliked",
            "comments",
            "group",
        ]

    # we are taking group from context as we need to get the actual group object not just the group id

    def create(self, validated_data):
        return BlogPost.objects.create(
            title=validated_data["title"],
            content=validated_data["content"],
            author=self.context["author"],
            group=self.context["group"],
        )


class BlogPostCommentSerializer(serializers.ModelSerializer):

    owner = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    disliked = serializers.SerializerMethodField()

    last_edited = serializers.SerializerMethodField()

    def get_last_edited(self, post):
        return post.last_edited.timestamp()

    def get_owner(self, comment):
        if self.context["request"].user.is_anonymous:
            return None

        return self.context["request"].user == comment.author

    author = serializers.CharField(source="author.username", read_only=True)
    profile_pic_url = serializers.SerializerMethodField()

    # profile pic url, if doesn't exists send empty string
    def get_profile_pic_url(self, blog):
        if blog.author.profile.profile_pic:
            return blog.author.profile.profile_pic.url
        return ""

    def get_liked(self, comment):
        request = self.context.get("request")

        if request.user.is_anonymous:
            return None

        return request.user in comment.liked_people.all()

    def get_disliked(self, comment):
        request = self.context.get("request")

        if request.user.is_anonymous:
            return None

        return request.user in comment.disliked_people.all()

    class Meta:
        model = BlogPostComment
        fields = [
            "id",
            "content",
            "post",
            "author",
            "profile_pic_url",
            "likes",
            "dislikes",
            "last_edited",
            "number_of_replies",
            "owner",
            "reply_to",
            "liked",
            "disliked",
        ]

        read_only_fields = [
            "id",
            "post",
            "likes",
            "dislikes",
            "last_edited",
            "replies",
            "liked",
            "disliked",
        ]

    def create(self, validated_data):
        return BlogPostComment.objects.create(
            author=self.context["author"],
            content=validated_data["content"],
            post=self.context["post"],
            reply_to=self.context["reply_to"],
        )


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ["image"]


class PostVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostVideo
        fields = ["video"]


class CarouselSerializer(serializers.HyperlinkedModelSerializer):

    author = serializers.CharField(source="author.username", read_only=True)
    profile_pic_url = serializers.SerializerMethodField()

    # profile pic url, if doesn't exists send empty string
    def get_profile_pic_url(self, blog):
        if blog.author.profile.profile_pic:
            return blog.author.profile.profile_pic.url
        return ""

    # To tell if a person has liked or disliked this post earlier
    liked = serializers.SerializerMethodField()
    disliked = serializers.SerializerMethodField()

    def get_liked(self, blog):
        """
        Returns True if the person has liked the post, false if didn't like the post, None if anonymous
        """
        request = self.context.get("request")

        if request.user.is_anonymous:
            return None

        return request.user in blog.liked_people.all()

    def get_disliked(self, blog):
        """
        Returns True if the person has disliked the post, false if didn't dislike the post, None if anonymous
        """
        request = self.context.get("request")

        if request.user.is_anonymous:
            return None

        return request.user in blog.disliked_people.all()

    owner = serializers.SerializerMethodField()

    def get_owner(self, blogpost):
        if self.context["request"].user.is_anonymous:
            return None

        return self.context["request"].user == blogpost.author

    content = serializers.SerializerMethodField()

    def get_content(self, post):
        return json.loads(post.content)

    post_url = serializers.HyperlinkedIdentityField(
        view_name="blogpost-detail", lookup_field="slug", read_only=True
    )

    comments = serializers.SerializerMethodField()

    def get_comments(self, post):
        return post.comments_carousel.all().count()

    # We want to convert datetime objects to unix time
    published = serializers.SerializerMethodField()
    last_edited = serializers.SerializerMethodField()

    def get_published(self, post):
        return post.published.timestamp()

    def get_last_edited(self, post):
        return post.last_edited.timestamp()

    post_type = serializers.ReadOnlyField(default="carousel")

    # we need to return group when deserializing
    group = serializers.CharField(source="group.name", read_only=True)

    def to_internal_value(self, data):
        internal = super(CarouselSerializer, self).to_internal_value(data)
        internal.update({"content": data["content"]})
        return internal

    class Meta:

        model = Carousel

        fields = [
            "id",
            "title",
            "content",
            "published",
            "last_edited",
            "author",
            "owner",
            "post_url",
            "profile_pic_url",
            "post_url",
            "likes",
            "dislikes",
            "comments",
            "liked",
            "disliked",
            "slug",
            "post_type",
            "group",
        ]

        read_only_fields = [
            "id",
            "author",
            "profile_pic_url",
            "published",
            "last_edited",
            "post_url",
            "likes",
            "dislikes",
            "liked",
            "diliked",
            "comments",
            "group",
        ]

    def create(self, validated_data):
        print("Validated data = ", validated_data)
        return Carousel.objects.create(
            title=validated_data["title"],
            content=validated_data["content"],
            author=self.context["author"],
            group=self.context["group"],
        )


class CarouselCommentSerializer(serializers.ModelSerializer):

    owner = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    disliked = serializers.SerializerMethodField()

    last_edited = serializers.SerializerMethodField()

    def get_last_edited(self, post):
        return post.last_edited.timestamp()

    def get_owner(self, comment):
        if self.context["request"].user.is_anonymous:
            return None

        return self.context["request"].user == comment.author

    author = serializers.CharField(source="author.username", read_only=True)
    profile_pic_url = serializers.CharField(
        source="author.profile.profile_pic.url", read_only=True
    )

    def get_liked(self, comment):
        request = self.context.get("request")

        if request.user.is_anonymous:
            return None

        return request.user in comment.liked_people.all()

    def get_disliked(self, comment):
        request = self.context.get("request")

        if request.user.is_anonymous:
            return None

        return request.user in comment.disliked_people.all()

    class Meta:
        model = CarouselComment
        fields = [
            "id",
            "content",
            "post",
            "author",
            "profile_pic_url",
            "likes",
            "dislikes",
            "last_edited",
            "number_of_replies",
            "owner",
            "reply_to",
            "liked",
            "disliked",
        ]

        read_only_fields = [
            "id",
            "post",
            "likes",
            "dislikes",
            "last_edited",
            "replies",
            "liked",
            "disliked",
        ]

    def create(self, validated_data):
        return CarouselComment.objects.create(
            author=self.context["author"],
            content=validated_data["content"],
            post=self.context["post"],
            reply_to=self.context["reply_to"],
        )
