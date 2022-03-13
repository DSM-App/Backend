from posts.serializers import (
    BlogPostSerializer,
    BlogPostCommentSerializer,
    CarouselSerializer,
    PostImageSerializer,
    PostVideoSerializer,
    CarouselCommentSerializer,
)
from rest_framework.views import APIView
from .permissions import ReadOnly, IsOwnerOrReadOnly
from .models import BlogPost, BlogPostComment, Carousel, CarouselComment
from rest_framework.response import Response
from rest_framework import permissions, status
from django.db.models import Q
from rest_framework.parsers import MultiPartParser, FormParser
from .utils import validate_signature
from groups.models import Group
import time


class BlogPostDetailView(APIView):

    permission_classes = [IsOwnerOrReadOnly]

    def get(self, request, slug):
        try:
            post = BlogPost.objects.get(slug=slug)
        except:
            return Response("Blog post not found", status=status.HTTP_400_BAD_REQUEST)

        post_retrieve_serializer = BlogPostSerializer(
            post, context={"request": request}
        )
        return Response(post_retrieve_serializer.data, status=status.HTTP_200_OK)

    def put(self, request, slug):
        try:
            post = BlogPost.objects.get(slug=slug)
        except:
            return Response("Blog post not found", status=status.HTTP_400_BAD_REQUEST)

        self.check_object_permissions(request, post)
        post_update_serializer = BlogPostSerializer(
            instance=post, data=request.data, context={"request": request}
        )
        if post_update_serializer.is_valid():
            post = post_update_serializer.save()
            return Response({"slug": post.slug}, status=status.HTTP_200_OK)
        return Response(
            post_update_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, slug):
        try:
            post = BlogPost.objects.get(slug=slug)
        except:
            return Response("Blog post not found", status=status.HTTP_400_BAD_REQUEST)

        self.check_object_permissions(request, post)
        post.delete()
        return Response(status=status.HTTP_200_OK)


class BlogPostCreateView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            group = Group.objects.get(id=request.data["groupId"])

        except Exception as e:
            print(e)
            return Response("Group not found", status=status.HTTP_404_NOT_FOUND)

        post_create_serializer = BlogPostSerializer(
            data=request.data, context={"author": request.user, "group": group}
        )
        if post_create_serializer.is_valid():
            post = post_create_serializer.save()
            return Response({"slug": post.slug}, status=status.HTTP_201_CREATED)
        return Response(
            post_create_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class HomepageBlogPostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        blogposts = BlogPost.objects.filter(
            Q(author__profile__in=request.user.profile.followings.all())
            | Q(author=request.user)
        )
        posts_list_serializer = BlogPostSerializer(
            blogposts, many=True, context={"request": request}
        )

        carouselposts = Carousel.objects.filter(
            Q(author__profile__in=request.user.profile.followings.all())
            | Q(author=request.user)
        )

        carousels_list_serializer = CarouselSerializer(
            carouselposts, many=True, context={"request": request}
        )

        blogposts_list = list(posts_list_serializer.data)
        carousels_list = list(carousels_list_serializer.data)

        blogposts_list.extend(carousels_list)
        posts = blogposts_list
        posts.sort(key=lambda post: -post["published"])

        return Response(posts, status=status.HTTP_200_OK)


class MyPostsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        posts = BlogPost.objects.filter(author=request.user)
        posts_list_serializer = BlogPostSerializer(
            posts, many=True, context={"request": request}
        )

        carouselposts = Carousel.objects.filter(Q(author=request.user))

        carousels_list_serializer = CarouselSerializer(
            carouselposts, many=True, context={"request": request}
        )

        blogposts_list = list(posts_list_serializer.data)
        carousels_list = list(carousels_list_serializer.data)

        blogposts_list.extend(carousels_list)
        posts = blogposts_list
        posts.sort(key=lambda post: -post["published"])
        return Response(posts, status=status.HTTP_200_OK)


class BlogPostLike(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        try:
            post = BlogPost.objects.get(slug=slug)
        except:
            return Response("Blog post not found", status=status.HTTP_400_BAD_REQUEST)

        post.like_post(request.user)
        return Response(status=status.HTTP_200_OK)


class BlogPostRemoveLike(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        try:
            post = BlogPost.objects.get(slug=slug)
        except:
            return Response("Blog post not found", status=status.HTTP_400_BAD_REQUEST)

        post.remove_like(request.user)
        return Response(status=status.HTTP_200_OK)


class BlogPostDislike(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        try:
            post = BlogPost.objects.get(slug=slug)
        except:
            return Response("Blog post not found", status=status.HTTP_400_BAD_REQUEST)

        post.dislike_post(request.user)
        return Response(status=status.HTTP_200_OK)


class BlogPostRemoveDislike(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        try:
            post = BlogPost.objects.get(slug=slug)
        except:
            return Response("Blog post not found", status=status.HTTP_400_BAD_REQUEST)

        post.remove_dislike(request.user)
        return Response(status=status.HTTP_200_OK)


class CommentListView(APIView):
    """
    Returns the list of comments for a given post and to create comment
    It returns only level 1 comments not replies
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        try:
            post = BlogPost.objects.get(id=id)
        except:
            return Response("post not found", status=status.HTTP_400_BAD_REQUEST)

        comment_list = post.comments.filter(reply_to=None)
        comment_list_serializer = BlogPostCommentSerializer(
            comment_list, many=True, context={"request": request}
        )
        return Response(comment_list_serializer.data, status=status.HTTP_200_OK)

    def post(self, request, id):
        """
        Post a new comment
        """

        try:
            post = BlogPost.objects.get(id=id)
        except:
            return Response("post not found", status=status.HTTP_400_BAD_REQUEST)

        reply_to = request.data.get("reply_to", None)

        # if reply_to exists it would be id chsnge it to actual comment instance
        if reply_to:
            reply_to = BlogPostComment.objects.get(id=reply_to)

        comment_create_serializer = BlogPostCommentSerializer(
            data=request.data,
            context={"author": request.user, "post": post, "reply_to": reply_to},
        )

        if comment_create_serializer.is_valid():
            new_comment = comment_create_serializer.save()
            # sending new comment in response body
            new_comment_serializer = BlogPostCommentSerializer(
                new_comment, context={"request": request}
            )
            return Response(new_comment_serializer.data, status=status.HTTP_200_OK)

        return Response(
            comment_create_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class CommentDetailView(APIView):

    permission_classes = [IsOwnerOrReadOnly]

    def get(self, request, id):
        """
        Returns all the replies to the comment
        """

        try:
            comment = BlogPostComment.objects.get(id=id)
        except:
            return Response("comment not found", status=status.HTTP_400_BAD_REQUEST)

        comment_replies = comment.replies.all()
        comment_replies_serializer = BlogPostCommentSerializer(
            comment_replies, many=True, context={"request": request}
        )

        return Response(comment_replies_serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        """
        Update the current comment
        """

        try:
            comment = BlogPostComment.objects.get(id=id)
        except:
            return Response("comment not found", status=status.HTTP_400_BAD_REQUEST)

        comment_update_serializer = BlogPostCommentSerializer(
            comment, data=request.data, context={"request": request}, partial=True
        )

        if comment_update_serializer.is_valid():
            comment_update_serializer.save()
            return Response(comment_update_serializer.data, status=status.HTTP_200_OK)
        return Response(
            comment_update_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, id):
        """
        Delete the comment
        """

        try:
            comment = BlogPostComment.objects.get(id=id)
        except:
            return Response("comment not found", status=status.HTTP_400_BAD_REQUEST)

        comment.delete()
        return Response(status=status.HTTP_200_OK)


class BlogPostCommentLikeView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        try:
            comment = BlogPostComment.objects.get(id=id)
        except:
            return Response("Comment not found", status=status.HTTP_400_BAD_REQUEST)

        comment.like(request.user)
        return Response(status=status.HTTP_200_OK)


class BlogPostCommentRemoveLikeView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        try:
            comment = BlogPostComment.objects.get(id=id)
        except:
            return Response("Comment not found", status=status.HTTP_400_BAD_REQUEST)

        comment.remove_like(request.user)
        return Response(status=status.HTTP_200_OK)


class BlogPostCommentDislikeView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        try:
            comment = BlogPostComment.objects.get(id=id)
        except:
            return Response("Comment not found", status=status.HTTP_400_BAD_REQUEST)

        comment.dislike(request.user)
        return Response(status=status.HTTP_200_OK)


class BlogPostCommentRemoveDislikeView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        try:
            comment = BlogPostComment.objects.get(id=id)
        except:
            return Response("Comment not found", status=status.HTTP_400_BAD_REQUEST)

        comment.remove_dislike(request.user)
        return Response(status=status.HTTP_200_OK)


class UploadPostImage(APIView):

    parser_classes = (
        MultiPartParser,
        FormParser,
    )

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # print(f"{request.META['CONTENT_TYPE']}")
        # print(f"request.data = {request.data}, ")
        # print(f"request.FILES = {request.FILES.items()}")

        postImageSerializer = PostImageSerializer(data=request.data)

        if postImageSerializer.is_valid():
            PostImage = postImageSerializer.save()
            print(PostImage)
            return Response(
                {"data": {"link": PostImage.image.url}}, status=status.HTTP_200_OK
            )

        return Response(postImageSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UploadPostVideo(APIView):

    parser_classes = (
        MultiPartParser,
        FormParser,
    )

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # print(f"{request.META['CONTENT_TYPE']}")
        # print(f"request.data = {request.data}, ")
        # print(f"request.FILES = {request.FILES.items()}")

        postVideoSerializer = PostVideoSerializer(data=request.data)

        if postVideoSerializer.is_valid():
            postVideo = postVideoSerializer.save()
            print(postVideo)
            return Response(
                {"data": {"link": postVideo.video.url}}, status=status.HTTP_200_OK
            )

        return Response(postVideoSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CarouselDetailView(APIView):

    permission_classes = [IsOwnerOrReadOnly]

    def get(self, request, slug):
        print(f"slug = {slug}")
        try:
            post = Carousel.objects.get(slug=slug)
        except:
            return Response(
                "Carousel post not found", status=status.HTTP_400_BAD_REQUEST
            )

        post_retrieve_serializer = CarouselSerializer(
            post, context={"request": request}
        )
        return Response(post_retrieve_serializer.data, status=status.HTTP_200_OK)

    def put(self, request, slug):
        try:
            post = Carousel.objects.get(slug=slug)
        except:
            return Response(
                "Carousel post not found", status=status.HTTP_400_BAD_REQUEST
            )

        self.check_object_permissions(request, post)
        post_update_serializer = CarouselSerializer(
            instance=post, data=request.data, context={"request": request}
        )
        if post_update_serializer.is_valid():
            post = post_update_serializer.save()
            return Response({"slug": post.slug}, status=status.HTTP_200_OK)
        return Response(
            post_update_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, slug):
        try:
            post = Carousel.objects.get(slug=slug)
        except:
            return Response(
                "Carousel post not found", status=status.HTTP_400_BAD_REQUEST
            )

        self.check_object_permissions(request, post)
        post.delete()
        return Response(status=status.HTTP_200_OK)


class CarouselCreateView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        print(request.data)

        try:
            group = Group.objects.get(id=request.data["groupId"])
        except Exception as e:
            print(e)
            return Response("Group not found", status=status.HTTP_404_NOT_FOUND)

        post_create_serializer = CarouselSerializer(
            data=request.data, context={"author": request.user, "group": group}
        )
        if post_create_serializer.is_valid():
            post = post_create_serializer.save()
            return Response({"slug": post.slug}, status=status.HTTP_201_CREATED)
        return Response(
            post_create_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class CarouselLike(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        try:
            post = Carousel.objects.get(slug=slug)
        except:
            return Response("Blog post not found", status=status.HTTP_400_BAD_REQUEST)

        post.like_post(request.user)
        return Response(status=status.HTTP_200_OK)


class CarouselRemoveLike(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        try:
            post = Carousel.objects.get(slug=slug)
        except:
            return Response("Blog post not found", status=status.HTTP_400_BAD_REQUEST)

        post.remove_like(request.user)
        return Response(status=status.HTTP_200_OK)


class CarouselDislike(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        try:
            post = Carousel.objects.get(slug=slug)
        except:
            return Response("Blog post not found", status=status.HTTP_400_BAD_REQUEST)

        post.dislike_post(request.user)
        return Response(status=status.HTTP_200_OK)


class CarouselRemoveDislike(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        try:
            post = Carousel.objects.get(slug=slug)
        except:
            return Response("Blog post not found", status=status.HTTP_400_BAD_REQUEST)

        post.remove_dislike(request.user)
        return Response(status=status.HTTP_200_OK)


class CarouselCommentListView(APIView):
    """
    Returns the list of comments for a given post and to create comment
    It returns only level 1 comments not replies
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        try:
            post = Carousel.objects.get(id=id)
        except:
            return Response("post not found", status=status.HTTP_400_BAD_REQUEST)

        comment_list = post.comments_carousel.filter(reply_to=None)
        comment_list_serializer = CarouselCommentSerializer(
            comment_list, many=True, context={"request": request}
        )
        return Response(comment_list_serializer.data, status=status.HTTP_200_OK)

    def post(self, request, id):
        """
        Post a new comment
        """

        try:
            post = Carousel.objects.get(id=id)
        except:
            return Response("post not found", status=status.HTTP_400_BAD_REQUEST)

        reply_to = request.data.get("reply_to", None)

        # if reply_to exists it would be id chsnge it to actual comment instance
        try:
            if reply_to:
                reply_to = CarouselComment.objects.get(id=reply_to)
        except:
            return Response(
                "parent comment does not exist", status=status.HTTP_400_BAD_REQUEST
            )

        comment_create_serializer = CarouselCommentSerializer(
            data=request.data,
            context={"author": request.user, "post": post, "reply_to": reply_to},
        )

        if comment_create_serializer.is_valid():
            new_comment = comment_create_serializer.save()
            # sending new comment in response body
            new_comment_serializer = CarouselCommentSerializer(
                new_comment, context={"request": request}
            )
            return Response(new_comment_serializer.data, status=status.HTTP_200_OK)

        return Response(
            comment_create_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class CarouselCommentDetailView(APIView):

    permission_classes = [IsOwnerOrReadOnly]

    def get(self, request, id):
        """
        Returns all the replies to the comment
        """

        try:
            comment = CarouselComment.objects.get(id=id)
        except:
            return Response("comment not found", status=status.HTTP_400_BAD_REQUEST)

        comment_replies = comment.replies_carousel.all()
        comment_replies_serializer = CarouselCommentSerializer(
            comment_replies, many=True, context={"request": request}
        )

        return Response(comment_replies_serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        """
        Update the current comment
        """

        try:
            comment = CarouselComment.objects.get(id=id)
        except:
            return Response("comment not found", status=status.HTTP_400_BAD_REQUEST)

        comment_update_serializer = CarouselCommentSerializer(
            comment, data=request.data, context={"request": request}, partial=True
        )

        if comment_update_serializer.is_valid():
            comment_update_serializer.save()
            return Response(comment_update_serializer.data, status=status.HTTP_200_OK)
        return Response(
            comment_update_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, id):
        """
        Delete the comment
        """

        try:
            comment = CarouselComment.objects.get(id=id)
        except:
            return Response("comment not found", status=status.HTTP_400_BAD_REQUEST)

        comment.delete()
        return Response(status=status.HTTP_200_OK)


class CarouselCommentLikeView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        try:
            comment = CarouselComment.objects.get(id=id)
        except:
            return Response("Comment not found", status=status.HTTP_400_BAD_REQUEST)

        comment.like(request.user)
        return Response(status=status.HTTP_200_OK)


class CarouselCommentRemoveLikeView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        try:
            comment = CarouselComment.objects.get(id=id)
        except:
            return Response("Comment not found", status=status.HTTP_400_BAD_REQUEST)

        comment.remove_like(request.user)
        return Response(status=status.HTTP_200_OK)


class CarouselCommentDislikeView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        try:
            comment = CarouselComment.objects.get(id=id)
        except:
            return Response("Comment not found", status=status.HTTP_400_BAD_REQUEST)

        comment.dislike(request.user)
        return Response(status=status.HTTP_200_OK)


class CarouselCommentRemoveDislikeView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        try:
            comment = CarouselComment.objects.get(id=id)
        except:
            return Response("Comment not found", status=status.HTTP_400_BAD_REQUEST)

        comment.remove_dislike(request.user)
        return Response(status=status.HTTP_200_OK)


class BlogPostValidateSignature(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):

        try:
            post = BlogPost.objects.get(id=id)
        except:
            return Response("Blogpost not found", status=status.HTTP_400_BAD_REQUEST)

        if validate_signature(
            post.signature_data(),
            post.digital_signature,
            post.author.profile.public_key,
        ):
            return Response("Singature is valid", status=status.HTTP_200_OK)
        return Response("Signature is invalid", status=status.HTTP_200_OK)


class CarouselValidateSignature(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):

        try:
            post = Carousel.objects.get(id=id)
        except:
            return Response("Carousel not found", status=status.HTTP_400_BAD_REQUEST)

        if validate_signature(
            post.signature_data(),
            post.digital_signature,
            post.author.profile.public_key,
        ):
            return Response("Singature is valid", status=status.HTTP_200_OK)
        return Response("Signature is invalid", status=status.HTTP_200_OK)
