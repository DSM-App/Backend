from django.contrib.auth import get_user_model
from django.utils.translation import deactivate_all
from posts.models import BlogPost
from posts.serializers import BlogPostSerializer

User = get_user_model()

u1, u2 = User.objects.all()

b1 = BlogPost.objects.all()[0]

s1 = BlogPostSerializer(b1, context={"request": None})

s1.data

data = {"title": "This is fifth post", "content": "This is content of fifth post"}

ds1 = BlogPostSerializer(data=data, context={"request": None})

ds1.is_valid()

ds1.validated_data
