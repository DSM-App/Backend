from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .serializers import GroupMembersSerializer, GroupSerializer, GroupDetailsSerializer
from .models import Group
from posts.serializers import BlogPostSerializer, CarouselSerializer
from rest_framework import generics
from django_filters import rest_framework as filters


class AddMember(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, groupId):
        """
        Adds a person to the group
        """
        try:
            group = Group.objects.get(id=groupId)
        except:
            return Response("Group does not exists", status=status.HTTP_404_NOT_FOUND)

        group.members.add(request.user)
        return Response(status=status.HTTP_200_OK)


class RemoveMember(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, groupId):
        """
        Removes a person from the group
        """

        try:
            group = Group.objects.get(id=groupId)
        except:
            return Response("Group does not exists", status=status.HTTP_404_NOT_FOUND)

        group.members.remove(request.user)
        return Response(status=status.HTTP_200_OK)


class GetAllMembers(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, groupId):
        """
        Returns all the members of a group
        """

        try:
            group = Group.objects.get(id=groupId)
        except:
            return Response("Group does not exists", status=status.HTTP_404_NOT_FOUND)

        group_members_list = GroupMembersSerializer(group.members.all(), many=True)
        return Response(group_members_list.data, status=status.HTTP_200_OK)


class GetAllGroupsOfUser(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Get all groups that a member is part of
        """

        user_groups_serializer = GroupSerializer(
            request.user.user_groups.all(), many=True
        )
        return Response(user_groups_serializer.data, status=status.HTTP_200_OK)


class GetAllBlogPosts(APIView):
    """
    Returns all blog posts of a group
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, groupId):

        try:
            group = Group.objects.get(id=groupId)
        except:
            return Response("Group does not exists", status=status.HTTP_404_NOT_FOUND)

        group_blogposts = BlogPostSerializer(
            group.group_blogposts.all(), context={"request": request}, many=True
        )

        return Response(group_blogposts.data, status=status.HTTP_200_OK)


class GetAllCarouselPosts(APIView):
    """
    Returns all carousel posts belonging to this group
    """

    def get(self, request, groupId):

        try:
            group = Group.objects.get(id=groupId)
        except:
            return Response("Group does not exists", status=status.HTTP_404_NOT_FOUND)

        group_carousels = CarouselSerializer(
            group.group_carousel.all(), context={"request": request}, many=True
        )

        return Response(group_carousels.data, status=status.HTTP_200_OK)


class GroupSearchFilter(filters.FilterSet):
    """
    Acts as filter for searching groups from query parameter
    """

    name = filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Group
        fields = ["name"]


class GroupSearchListView(generics.ListAPIView):
    """
    Uses the GroupSearchFilter to filter the groups based on query parameters
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = GroupSearchFilter


class GroupDetailsView(APIView):
    """
    Sends group meta data
    """

    def get(self, request, group_name):
        try:
            group = Group.objects.get(name=group_name)
        except:
            return Response("Group does not exists", status=status.HTTP_404_NOT_FOUND)

        group_details = GroupDetailsSerializer(group, context={"request": request})
        return Response(group_details.data, status=status.HTTP_200_OK)


class GroupHomePageView(APIView):
    """
    Returns all the posts - (blogposts and carousels belonging to that group)
    """

    def get(self, request, group_name):
        try:
            group = Group.objects.get(name=group_name)
        except:
            return Response("Group does not exists", status=status.HTTP_404_NOT_FOUND)

        BlogPostSerializer(
            group.group_blogposts.all(), context={"request": request}, many=True
        )
        blog_posts_serializer = BlogPostSerializer(
            group.group_blogposts.all(), context={"request": request}, many=True
        )

        blogposts_list = list(blog_posts_serializer.data)

        carousels_serializer = CarouselSerializer(
            group.group_carousel.all(), context={"request": request}, many=True
        )

        carousels_list = list(carousels_serializer.data)

        blogposts_list.extend(carousels_list)
        posts = blogposts_list
        posts.sort(key=lambda post: -post["published"])

        return Response(posts, status=status.HTTP_200_OK)
