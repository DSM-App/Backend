from django.urls import path, include
from .views import (
    ProfilePage,
    ProfilePictureUpload,
    ChangeEmailRequest,
    ChangeEmailVerify,
    ChangeUsername,
    ProfileDetailView,
)


urlpatterns = [
    path("profile/detail-info/", ProfileDetailView.as_view()),
    path("profile-pic-upload/", ProfilePictureUpload.as_view()),
    path("profile/change-email-request/", ChangeEmailRequest.as_view()),
    path("profile/change-email-verify/", ChangeEmailVerify.as_view()),
    path("profile/change-username/", ChangeUsername.as_view()),
    path("profile/<str:username>/", ProfilePage.as_view()),
]
