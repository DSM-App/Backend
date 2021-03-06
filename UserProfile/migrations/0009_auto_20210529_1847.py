# Generated by Django 3.2.3 on 2021-05-29 18:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("UserProfile", "0008_auto_20210525_0557"),
    ]

    operations = [
        migrations.CreateModel(
            name="Follow",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(default="", max_length=200)),
                ("last_name", models.CharField(default="", max_length=200)),
                (
                    "followers",
                    models.ManyToManyField(
                        related_name="followings",
                        through="UserProfile.Follow",
                        to="UserProfile.Profile",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="follow",
            name="from_profile",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="from_profile",
                to="UserProfile.profile",
            ),
        ),
        migrations.AddField(
            model_name="follow",
            name="to_profile",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="to_profile",
                to="UserProfile.profile",
            ),
        ),
    ]
