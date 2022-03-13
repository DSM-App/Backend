from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.deletion import SET_NULL
from groups.models import Group
from posts.models import BlogPost, Carousel

User = get_user_model()


class Vote(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(max_length=5000, default="")

    def __str__(self):
        return "Vote " + str(self.id) + " " + str(self.comment)


class OwnershipCopyRights(models.Model):
    copyrighted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reason = models.TextField(max_length=10000, default="")
    copyrighted_votes = models.ManyToManyField(Vote, related_name="copyrights_voted")
    not_copyrighted_votes = models.ManyToManyField(
        Vote, related_name="not_copyrights_voted"
    )
    closed = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(Group, on_delete=SET_NULL, null=True)
    blogpost = models.ForeignKey(BlogPost, on_delete=models.SET_NULL, null=True)
    carousel = models.ForeignKey(Carousel, on_delete=models.SET_NULL, null=True)

    @property
    def number_of_copyrighted_votes(self):
        return self.copyrighted_votes.all().count()

    @property
    def number_of_not_copyrighted_votes(self):
        return self.not_copyrighted_votes.all().count()

    def __str__(self):
        if self.blogpost:
            return (
                "Copyright " + str(self.id) + " on blogpost " + str(self.blogpost.slug)
            )
        elif self.carousel:
            return (
                "Copyright " + str(self.id) + " on carousel " + str(self.carousel.slug)
            )
        else:
            return "Copyright " + str(self.id) + " on post X"
