from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from .models import BlogPost, Carousel
from .utils import generate_digital_signature


@receiver(post_save, sender=BlogPost)
def initiate_digital_signature(sender, instance, created, *args, **kwargs):
    if created:
        """
        It will run only once when created
        Since published time is not available before saving it will just initiate the save
        And actual digital signature is generated by pre_save
        """
        print("signature initiated in post save")

        instance.save()


@receiver(pre_save, sender=BlogPost)
def create_digital_signature(sender, instance, *args, **kwargs):

    """
    It will set actual digital signature of the post
    We need published field to create / update the digital signature
    """

    if instance.published:
        data = instance.signature_data()
        digital_signature = generate_digital_signature(
            data, instance.author.profile.private_key
        )
        print("signature updated in pre save")
        print("digital signature = ", digital_signature)

        instance.digital_signature = digital_signature


@receiver(post_save, sender=Carousel)
def initiate_digital_signature(sender, instance, created, *args, **kwargs):
    if created:
        instance.save()


@receiver(pre_save, sender=Carousel)
def create_digital_signature(sender, instance, *args, **kwargs):

    if instance.published:
        data = instance.signature_data()
        digital_signature = generate_digital_signature(
            data, instance.author.profile.private_key
        )

        instance.digital_signature = digital_signature