from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.contrib.auth.models import UserManager
from django.contrib.auth import get_user_model
from PIL import Image


# Overriding the User model
class CustomAccountManager(BaseUserManager):
    def create_superuser(self, email, username, password, **other_fields):

        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_superuser", True)
        other_fields.setdefault("is_active", True)

        if other_fields.get("is_staff") is not True:
            raise ValueError("Superuser must be assigned to is_staff=True.")
        if other_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must be assigned to is_superuser=True.")

        return self.create_user(email, username, password, **other_fields)

    def create_user(self, email, username, password, **other_fields):
        print("CREATING USER FROM create_user")
        if not email:
            raise ValueError(_("You must provide an email address"))

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **other_fields)
        user.set_password(password)
        user.save()
        return user


# Create your models here.


class CustomUser(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(max_length=150, unique=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = CustomAccountManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username


class Profile(models.Model):
    def upload_path(instance, filename):
        return f"{instance.user.id}/profile_pics/{filename}"

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    first_name = models.CharField(max_length=200, default="")
    last_name = models.CharField(max_length=200, default="")
    followers = models.ManyToManyField(
        "self", symmetrical=False, through="Follow", related_name="followings"
    )
    profile_pic = models.ImageField(upload_to=upload_path, null=True)
    follow_requests_received = models.ManyToManyField(
        "self", symmetrical=False, related_name="follow_requests_sent"
    )
    bio = models.CharField(max_length=5000, default="")

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def save(self, *args, **kwargs):
        """
        To reduce the dimensions of the image
        """
        # TODO: currently not taking care of aspect ratio, take care of it

        super().save(*args, **kwargs)

        if self.profile_pic:
            img = Image.open(self.profile_pic.path)

            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.profile_pic.path)

    @property
    def number_of_followers(self):
        return self.followers.all().count()

    @property
    def number_of_followings(self):
        return self.followings.all().count()

    @property
    def accept_follow_request(self, user):

        """
        To accept a follow request, check if the user exists in your follow_requests_received
        and obviously you cannot send or accept follow request to yourself
        """

        if user != self.user and user in self.follow_requests_received.all():
            self.followers.add(user)
            self.follow_requests_received.remove(user)

    @property
    def decline_follow_request(self, user):

        """
        To decline a follow request that user must be in your follow_request_received list
        """

        if user != self.user and user in self.follow_requests_received.all():
            self.follow_requests_received.remove(user)

    @property
    def send_follow_request(self, user):
        """
        To send a follow request only check is you cannot send a follow request to yourself
        and you must not be already following that person
        """

        if user != self.user and user not in self.followings.all():
            self.follow_requests_sent.add(user)

    @property
    def takeback_follow_request(self, user):
        """
        To takeback a follow request you must have sent a follow request earlier to that user
        """

        if user != self.user and user in self.follow_requests_sent.all():
            self.follow_requests_sent.remove(user)

    @property
    def unfollow(self, user):
        """
        To unfollow a user you must be following him already
        """

        if user != self.user and user in self.followings.all():
            self.followings.remove(user)

    @property
    def remove_follower(self, user):
        """
        To remove a user from your followers list, the user must be already following you
        """

        if user != self.user and user in self.followers.all():
            self.followers.remove(user)


class Follow(models.Model):
    from_profile = models.ForeignKey(
        Profile, related_name="from_profile", on_delete=models.CASCADE
    )
    to_profile = models.ForeignKey(
        Profile, related_name="to_profile", on_delete=models.CASCADE
    )


class EmailUpdateToken(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    new_email = models.EmailField(max_length=250)
    token = models.CharField(max_length=100)
    expires_at = models.DateTimeField()
