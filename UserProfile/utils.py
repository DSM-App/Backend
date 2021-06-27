from .models import EmailUpdateToken
from datetime import timedelta
from django.utils import timezone
import random
from django.conf import settings
from django.core.mail import send_mail

# Random number for OTP
def get_random_six_digit_token():
    return random.randint(100000, 999999)


def create_email_update_token(user, new_email):
    """
    A function which generates an OTP and new_email and stores it in database
    """

    # Delete any previous tokens if possible to avoid confusion
    EmailUpdateToken.objects.filter(user__id=user.id).delete()

    # Create a new token
    token_obj = EmailUpdateToken.objects.create(
        user=user,
        new_email=new_email,
        token=get_random_six_digit_token(),
        expires_at=timezone.now() + timedelta(seconds=300),
    )

    # Send token as email to new_email

    send_mail(
        # title:
        "Email Change OTP for {title}".format(title="Decentralized Social Media"),
        # message
        """Heeyy {},  {} Here is your OTP {} for email change""".format(
            user.username, "Decentralized Social Media", token_obj.token
        ),
        # from:
        settings.EMAIL_HOST_USER,
        # to
        [new_email],
    )
