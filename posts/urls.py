from django.urls import path, include
from .views import (
    BlogPostDetailView,
    BlogPostCreateView,
    BlogPostLike,
    BlogPostRemoveLike,
    BlogPostDislike,
    BlogPostRemoveDislike,
    HomepageBlogPostView,
    MyPostsView,
    CommentListView,
    CommentDetailView,
    BlogPostCommentLikeView,
    BlogPostCommentDislikeView,
    BlogPostCommentRemoveLikeView,
    BlogPostCommentRemoveDislikeView,
    UploadPostImage,
    UploadPostVideo,
    CarouselCreateView,
    CarouselDetailView,
    CarouselLike,
    CarouselRemoveLike,
    CarouselDislike,
    CarouselRemoveDislike,
    CarouselCommentListView,
    CarouselCommentDetailView,
    CarouselCommentLikeView,
    CarouselCommentDislikeView,
    CarouselCommentRemoveLikeView,
    CarouselCommentRemoveDislikeView,
    BlogPostValidateSignature,
    CarouselValidateSignature,
)

urlpatterns = [
    # posts
    path("home-page/", HomepageBlogPostView.as_view()),
    path("my-posts/", MyPostsView.as_view()),
    path("blogpost/", BlogPostCreateView.as_view()),
    path("blogpost/like/<str:slug>/", BlogPostLike.as_view()),
    path("blogpost/remove-like/<str:slug>/", BlogPostRemoveLike.as_view()),
    path("blogpost/dislike/<str:slug>/", BlogPostDislike.as_view()),
    path("blogpost/remove-dislike/<str:slug>/", BlogPostRemoveDislike.as_view()),
    path("blogpost/upload-image/", UploadPostImage.as_view()),
    path("blogpost/upload-video/", UploadPostVideo.as_view()),
    path("blogpost/validate-signature/<int:id>/", BlogPostValidateSignature.as_view()),
    path("blogpost/<str:slug>/", BlogPostDetailView.as_view(), name="blogpost-detail"),
    # comments
    path(
        "blogpost/<int:id>/comments/", CommentListView.as_view()
    ),  # to get comments of a given post id
    path(
        "blogpost/comment/<int:id>/", CommentDetailView.as_view()
    ),  # to get reply comments of a given comment id
    path("blogpost/comment/like/<int:id>/", BlogPostCommentLikeView.as_view()),
    path(
        "blogpost/comment/remove-like/<int:id>/",
        BlogPostCommentRemoveLikeView.as_view(),
    ),
    path("blogpost/comment/dislike/<int:id>/", BlogPostCommentDislikeView.as_view()),
    path(
        "blogpost/comment/remove-dislike/<int:id>/",
        BlogPostCommentRemoveDislikeView.as_view(),
    ),
    path("carousel/", CarouselCreateView.as_view()),
    path("carousel/like/<str:slug>/", CarouselLike.as_view()),
    path("carousel/remove-like/<str:slug>/", CarouselRemoveLike.as_view()),
    path("carousel/dislike/<str:slug>/", CarouselDislike.as_view()),
    path("carousel/remove-dislike/<str:slug>/", CarouselRemoveDislike.as_view()),
    path("carousel/validate-signature/<int:id>/", CarouselValidateSignature.as_view()),
    path("carousel/<str:slug>/", CarouselDetailView.as_view()),
    path(
        "carousel/<int:id>/comments/", CarouselCommentListView.as_view()
    ),  # to get comments of a given post id
    path("carousel/comment/<int:id>/", CarouselCommentDetailView.as_view()),
    path("carousel/comment/like/<int:id>/", CarouselCommentLikeView.as_view()),
    path(
        "carousel/comment/remove-like/<int:id>/",
        CarouselCommentRemoveLikeView.as_view(),
    ),
    path("carousel/comment/dislike/<int:id>/", CarouselCommentDislikeView.as_view()),
    path(
        "carousel/comment/remove-dislike/<int:id>/",
        CarouselCommentRemoveDislikeView.as_view(),
    ),
]
