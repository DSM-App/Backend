from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import Profile
from django.db.models.signals import post_save


@receiver(post_save, sender=get_user_model())
def create_profile(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        # print(F"Profile created for user = {instance.username}")
        # send_mail(
        #     # title
        #     "Your account is activated",

        #     # message
        #     """Your account has been successfully activated.
        #         Please customize your profile.
        #     """,

        #     # from
        #     settings.EMAIL_HOST_USER,

        #     # to
        #     [instance.email],

        # )
