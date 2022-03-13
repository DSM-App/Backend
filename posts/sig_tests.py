from posts.models import BlogPost, Carousel
from django.contrib.auth import get_user_model

User = get_user_model()

s = User.objects.get(username="san")

b = BlogPost.objects.create(title="hello", content="content", author=s)

from posts.utils import validate_signature

print(
    validate_signature(
        b.signature_data(), b.digital_signature, b.author.profile.public_key
    )
)
