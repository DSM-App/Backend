from django.contrib.auth import get_user_model
from UserProfile.serializers import UserListSerializer
from UserProfile.models import Profile

User = get_user_model()

users = User.objects.all()[0]

profiles = Profile.objects.all()[0]

us = UserListSerializer(profiles)

print(us.data)
