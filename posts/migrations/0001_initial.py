# Generated by Django 3.2.3 on 2021-06-29 09:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="BlogPost",
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
                ("title", models.CharField(max_length=300)),
                ("content", models.CharField(max_length=10000)),
                ("published", models.DateTimeField(auto_now=True)),
                ("last_edited", models.DateTimeField(auto_now_add=True)),
                ("slug", models.SlugField(blank=True, max_length=100, unique=True)),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "disliked_people",
                    models.ManyToManyField(
                        related_name="disliked_posts", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "liked_people",
                    models.ManyToManyField(
                        related_name="liked_posts", to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
        ),
    ]
