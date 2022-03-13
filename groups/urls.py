from django.urls import path, include
from .views import (
    AddMember,
    RemoveMember,
    GetAllMembers,
    GetAllGroupsOfUser,
    GetAllBlogPosts,
    GetAllCarouselPosts,
    GroupSearchListView,
    GroupDetailsView,
    GroupHomePageView,
)

urlpatterns = [
    path("add/<int:groupId>/", AddMember.as_view()),
    path("remove/<int:groupId>/", RemoveMember.as_view()),
    path("members/<int:groupId>/", GetAllMembers.as_view()),
    path("user-groups/", GetAllGroupsOfUser.as_view()),
    path("group-blogposts/<int:groupId>/", GetAllBlogPosts.as_view()),
    path("group-carousels/<int:groupId>/", GetAllCarouselPosts.as_view()),
    path("group-search/", GroupSearchListView.as_view()),
    path("details/<str:group_name>/", GroupDetailsView.as_view()),
    path("group-posts/<str:group_name>/", GroupHomePageView.as_view()),
]
