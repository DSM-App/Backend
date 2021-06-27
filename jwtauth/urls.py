# jwtauth/urls.py

from django.urls import path
from django.urls import path, include
from .views import registration, login, ChangePasswordView, VerifyEmailView, LogoutView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("register/", registration, name="register"),
    path("login/", login, name="login"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify_email"),
    path(
        "password-reset/",
        include("django_rest_passwordreset.urls", namespace="password_reset"),
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
]
