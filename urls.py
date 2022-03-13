from django.urls import path, include
from .views import (
    CopyrightsCreateView,
    CopyrightDetails,
    VoteCreateView,
    VoteUpdateView,
    CopyrightVotes
)

urlpatterns = [
    path("", CopyrightsCreateView.as_view()),
    path("<int:copyright_id>/", CopyrightDetails.as_view()),
    path("create-vote/<int:copyright_id>/", VoteCreateView.as_view()),
    path("update-vote/<int:vote_id>/", VoteUpdateView.as_view()),
    path("get-all-votes/<int:copyright_id>/",CopyrightVotes.as_view())
]
