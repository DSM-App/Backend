from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .models import OwnershipCopyRights, Vote
from groups.models import Group
from django.contrib.auth import get_user_model
from posts.models import BlogPost, Carousel
from .serializers import (
    OwnershipCopyRightsSerializer,
    OwnershipCopyRightsDetailsSerializer,
    VoteDetailsSerializer,
)

User = get_user_model()


class CopyrightsCreateView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            group = Group.objects.get(id=request.data["groupId"])

        except Exception as e:
            print(e)
            return Response("Group not found", status=status.HTTP_404_NOT_FOUND)

        try:
            if request.data["post_type"] == "blogpost":
                post = BlogPost.objects.get(id=request.data["post_id"])
            elif request.data["post_type"] == "carousel":
                post = Carousel.objects.get(id=request.data["post_id"])
        except Exception as e:
            print(e)
            return Response("Post not found", status=status.HTTP_404_NOT_FOUND)

        context = {
            "copyrighted_by": request.user,
            "group": group,
            "blogpost": post if request.data["post_type"] == "blogpost" else None,
            "carousel": post if request.data["post_type"] == "carousel" else None,
        }
        print("context = ", context)
        copyright_create_serializer = OwnershipCopyRightsSerializer(
            data=request.data,
            context=context,
        )

        if copyright_create_serializer.is_valid():
            copyright = copyright_create_serializer.save()
            return Response(copyright.id, status=status.HTTP_201_CREATED)
        return Response(
            copyright_create_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class CopyrightDetails(APIView):
    def get(self, request, copyright_id):
        try:
            copyright = OwnershipCopyRights.objects.get(id=copyright_id)
        except:
            return Response("Copyright not found", status=status.HTTP_404_NOT_FOUND)

        copyright_details_serializer = OwnershipCopyRightsDetailsSerializer(copyright)
        return Response(copyright_details_serializer.data, status=status.HTTP_200_OK)


class VoteCreateView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, copyright_id):

        try:
            copyright = OwnershipCopyRights.objects.get(id=copyright_id)
        except:
            return Response("Copyright not found", status=status.HTTP_404_NOT_FOUND)

        # Only miners are allowed to vote
        if request.user not in copyright.group.miners.all():
            return Response("Only miners can vote", status=status.HTTP_400_BAD_REQUEST)

        # A miner can vote only once
        for vote in copyright.copyrighted_votes.all():
            if vote.author == request.user:
                return Response(
                    "You have already voted, you can edit your vote instead of creating new vote",
                    status=status.HTTP_400_BAD_REQUEST,
                )

        for vote in copyright.not_copyrighted_votes.all():
            if vote.author == request.user:
                return Response(
                    "You have already voted, you can edit your vote instead of creating new vote",
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            vote = Vote.objects.create(
                author=request.user,
                comment=request.data["comment"],
            )
        except Exception as e:
            print(e)
            return Response("Failded to create vote", status=status.HTTP_404_NOT_FOUND)

        if request.data["is_copyrighted"]:
            copyright.copyrighted_votes.add(vote)
        else:
            copyright.not_copyrighted_votes.add(vote)

        copyright_details_serializer = OwnershipCopyRightsDetailsSerializer(copyright)

        return Response(
            copyright_details_serializer.data, status=status.HTTP_201_CREATED
        )


class VoteUpdateView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, vote_id):

        try:
            vote = Vote.objects.get(id=vote_id)
        except:
            return Response("Vote not found", status=status.HTTP_404_NOT_FOUND)

        # Only author of vate can edit
        print("user = ", request.user)
        print("author = ", vote.author)
        if request.user != vote.author:
            return Response(
                "Only author can edit the vote", status=status.HTTP_401_UNAUTHORIZED
            )

        copyright_id = request.data["copyright_id"]

        try:
            copyright = OwnershipCopyRights.objects.get(id=copyright_id)
        except:
            return Response("Copyright not found", status=status.HTTP_404_NOT_FOUND)

        # Only miners are allowed to vote
        if request.user not in copyright.group.miners.all():
            return Response("Only miners can vote", status=status.HTTP_400_BAD_REQUEST)

        # We have to clear the old vote before adding new one
        copyright.not_copyrighted_votes.remove(Vote.objects.get(id=vote_id))
        copyright.copyrighted_votes.remove(Vote.objects.get(id=vote_id))

        copyright.save()

        # Let's edit the current vote
        vote.comment = request.data["comment"]
        vote.save()

        # Now add the new vote
        if request.data["is_copyrighted"]:
            copyright.copyrighted_votes.add(vote)
        else:
            copyright.not_copyrighted_votes.add(vote)

        copyright.save()

        copyright_details_serializer = OwnershipCopyRightsDetailsSerializer(copyright)

        return Response(
            copyright_details_serializer.data, status=status.HTTP_201_CREATED
        )


class CopyrightVotes(APIView):
    """
    Returns all votes of a given copyright
    """

    def get(self, request, copyright_id):

        try:
            copyright = OwnershipCopyRights.objects.get(id=copyright_id)
        except:
            return Response("Copyright not found", status=status.HTTP_404_NOT_FOUND)

        print(
            "copyrights not copyrighted votes = ", copyright.not_copyrighted_votes.all()
        )
        copyrighted_votes = VoteDetailsSerializer(
            copyright.copyrighted_votes.all(), many=True
        )
        not_copyrighted_votes = VoteDetailsSerializer(
            copyright.not_copyrighted_votes.all(), many=True
        )

        return Response(
            {
                "copyrighted_votes": copyrighted_votes.data,
                "not_copyrighted_votes": not_copyrighted_votes.data,
            },
            status=status.HTTP_200_OK,
        )
