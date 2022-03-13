from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.constraints import UniqueConstraint

# from posts.models import BlogPost, Carousel


User = get_user_model()

# https://source.unsplash.com/random


class Group(models.Model):
    def upload_path(instance, filename):
        return f"{instance.id}/groups/{filename}"

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=10000, default="")
    members = models.ManyToManyField(User, related_name="user_groups")
    miners = models.ManyToManyField(User, related_name="miners_in_groups")
    created_at = models.DateTimeField(auto_now_add=True)

    election_participants = models.ManyToManyField(
        User, related_name="group_election_participants"
    )

    icon = models.ImageField(
        upload_to=upload_path, default="https://source.unsplash.com/random"
    )
    banner = models.ImageField(
        upload_to=upload_path, default="https://source.unsplash.com/random"
    )

    def __str__(self):
        return f"{self.name}"

    @property
    def number_of_people(self):
        return self.members.count()

    @property
    def number_of_miners(self):
        return self.miners.count()

    def add_member(self, user):
        self.members.add(user)

    def remove_member(self, user):
        self.members.remove(user)

    def add_miner(self, user):
        self.miners.add(user)

    def remove_miner(self, user):
        self.miners.remove(user)

    @property
    def total_power(self):
        """
        Calculates the sum of power of all the group members
        Since it is a changing value, it has to be calculated for each call
        """
        power = 0
        for user in self.members.all():
            power += user.profile.total_power 
        return power if power != 0 else 1