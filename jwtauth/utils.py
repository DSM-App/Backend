import random
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from .models import EmailVerificationTokens


# Random number for OTP
def get_random_six_digit_token():
    return random.randint(100000, 999999)


# Password Vaidator
def password_check(passwd):

    SpecialSym = ["$", "@", "#", "%"]

    if len(passwd) < 6:
        raise Exception("length should be at least 6")

    if len(passwd) > 20:
        raise Exception("length should be not be greater than 20")

    if not any(char.isdigit() for char in passwd):
        raise Exception("Password should have at least one numeral")

    if not any(char.isupper() for char in passwd):
        raise Exception("Password should have at least one uppercase letter")

    if not any(char.islower() for char in passwd):
        raise Exception("Password should have at least one lowercase letter")

    # if not any(char in SpecialSym for char in passwd):
    #    raise Exception('Password should have at least one of the symbols $@#')


def send_verify_emai(user, email):
    # Delete all the previous tokens of same user

    EmailVerificationTokens.objects.filter(user__email=email).delete()

    token_obj = EmailVerificationTokens.objects.create(
        user=user,
        token=get_random_six_digit_token(),
        expires_at=timezone.now() + timedelta(seconds=300),
    )
    token_obj.save()
    print(settings.EMAIL_HOST_USER)
    send_mail(
        # title:
        "Email Verification for for {title}".format(title="Decentralized Social Media"),
        # message
        """Heeyy {}, Welcome to {} Here is your OTP {}
            """.format(
            user.username, "Decentralized Social Media", token_obj.token
        ),
        # from:
        settings.EMAIL_HOST_USER,
        # to
        [email],
    )
