from posts.models import BlogPost, BlogPostComment
from django.contrib.auth import get_user_model

User = get_user_model()

ps = BlogPost.objects.all()
us = User.objects.all() 

u1, u2 = us[0], us[1]
p1, p2 = ps[0], ps[1] 

c = BlogPostComment(author = u1, content = "THis is technically first comment to be saved", post = p1)