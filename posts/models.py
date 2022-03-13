from django.contrib import auth
from posts.utils import unique_slugify
from django.db import models
from django.contrib.auth import get_user_model
from .utils import unique_slugify
from UserProfile.models import Profile
from groups.models import Group


User = get_user_model()


class BlogPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    content = models.CharField(max_length=100000)
    published = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, max_length=100, blank=True)
    liked_people = models.ManyToManyField(User, related_name="liked_posts")
    disliked_people = models.ManyToManyField(User, related_name="disliked_posts")
    post_points = models.FloatField(default=0.0)
    digital_signature = models.BinaryField(null=True, blank=True)
    group = models.ForeignKey(
        Group, on_delete=models.RESTRICT, null=True, related_name="group_blogposts"
    )

    def __str__(self):
        return f"{self.title}"

    def save(self, **kwargs):
        unique_slugify(self, self.title)
        super(BlogPost, self).save(**kwargs)

    def signature_data(self):
        """
        returns that data for making digital signature
        only some suitable fields of the post are considered for making digital signatures
        """

        return {
            "title": self.title,
            "content": self.content,
            "published": self.published.timestamp(),
            "author": self.author.id,
        }

    def like_post(self, user):
        """
        This property is used when a user wants to like a post
        NOTE: we don't have to take care if the user has already liked the post or not
        if the user again somehow executes this method. His name won't we added again to the list

        Also a person cannot like and dislike a post at the same time. So we need to check if the person
        has disliked we will remove the person from the list
        """

        author = self.author  # author of the post
        group = self.group        # group in which it was posted
        total_power_of_group = group.total_power

        # Now since the user is liking it we need to increment it again

        total_power_of_group = group.total_power
        author.temporary_power += user.total_power / total_power_of_group 
        author.save()
        self.disliked_people.remove(user)
        self.liked_people.add(user)

    def dislike_post(self, user):

        author = self.author  
        group = self.group        
        total_power_of_group = group.total_power

        author.temporary_power -= user.total_power / total_power_of_group 
        author.save()
        self.disliked_people.add(user)
        self.liked_people.remove(user)

    def remove_like(self, user):
        """
        When user wants to takeback his like on a post
        """

        author = self.author  
        group = self.group        
        total_power_of_group = group.total_power

        # Decrease the poweronly if the user had previously liked it
        if user in self.liked_people.all():
            author.temporary_power -= user.total_power / total_power_of_group 
            author.save()
            self.liked_people.remove(user)


    def remove_dislike(self, user):
        """
        When the user wants to takeback his dislike on a post
        """

        author = self.author  
        group = self.group        
        total_power_of_group = group.total_power

        # Increase the poweronly if the user had previously disliked it
        if user in self.disliked_people.all():
            author.temporary_power += user.total_power / total_power_of_group 
            author.save()
            self.disliked_people.remove(user)


    @property
    def likes(self):
        """
        Returns the number of likes
        """
        return self.liked_people.all().count()

    @property
    def dislikes(self):
        """
        Returns the number of dislikes
        """
        return self.disliked_people.all().count()


class BlogPostComment(models.Model):

    """
    A model to store comments - only 1 level of nesting is aloowed, afterwards replies are referred by @username
    """

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=10000)
    liked_people = models.ManyToManyField(User, related_name="liked_comments")
    disliked_people = models.ManyToManyField(User, related_name="disliked_comments")
    published = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)
    post = models.ForeignKey(
        BlogPost, on_delete=models.CASCADE, related_name="comments"
    )
    reply_to = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, related_name="replies"
    )  # a comment can be a reply to another comment

    def __str__(self):
        return f"{self.content}"

    def like(self, user):
        self.disliked_people.remove(user)
        self.liked_people.add(user)

    def remove_like(self, user):
        """
        When user wants to takeback his like on a post
        """
        self.liked_people.remove(user)

    def dislike(self, user):
        self.liked_people.remove(user)
        self.disliked_people.add(user)

    def remove_dislike(self, user):
        self.disliked_people.remove(user)

    @property
    def likes(self):
        """
        Returns the number of likes
        """
        return self.liked_people.all().count()

    @property
    def dislikes(self):
        """
        Returns number of dislikes
        """
        return self.disliked_people.all().count()

    @property
    def number_of_replies(self):
        """
        Returns the number of replies
        """

        return self.replies.all().count()


class PostImage(models.Model):
    """
    Model to store post images - since images have to be saved even before the
    actual post is saved
    """

    def upload_path(instance, filename):
        return f"post-images/{filename}"

    image = models.ImageField(upload_to=upload_path)


class PostVideo(models.Model):
    """
    Videos are uploaded and saved. Viodeo can be a part of carousel which has photos and videos
    """

    video = models.FileField(upload_to="videos/")


class Carousel(models.Model):
    """
    For carousel post. A coursel contains of slideable images and videos.
    It is also a type of post. in place of content it store's URL's of images and videos
    """

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    content = models.CharField(max_length=100000)
    published = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, max_length=100, blank=True)
    liked_people = models.ManyToManyField(User, related_name="liked_carousels")
    disliked_people = models.ManyToManyField(User, related_name="disliked_carousels")
    post_points = models.FloatField(default=0.0)
    digital_signature = models.BinaryField(null=True, blank=True)
    group = models.ForeignKey(
        Group, on_delete=models.RESTRICT, null=True, related_name="group_carousel"
    )

    def __str__(self):
        return f"{self.title}"

    def save(self, **kwargs):
        unique_slugify(self, self.title)
        super(Carousel, self).save(**kwargs)

    def signature_data(self):
        """
        returns that data for making digital signature
        only some suitable fields of the post are considered for making digital signatures
        """

        return {
            "title": self.title,
            "content": self.content,
            "published": self.published.timestamp(),
            "author": self.author.id,
        }

    def like_post(self, user):
        """
        This property is used when a user wants to like a post
        NOTE: we don't have to take care if the user has already liked the post or not
        if the user again somehow executes this method. His name won't we added again to the list

        Also a person cannot like and dislike a post at the same time. So we need to check if the person
        has disliked we will remove the person from the list
        """

        self.liked_people.add(user)
        self.disliked_people.remove(user)
        self.power = self.power + 0.2 * user.power

    def dislike_post(self, user):

        self.disliked_people.add(user)
        self.liked_people.remove(user)
        self.power = self.power - 0.2 * user.power

    def remove_like(self, user):
        """
        When user wants to takeback his like on a post
        """

        self.liked_people.remove(user)
        self.power = self.power - 0.2 * user.power

    def remove_dislike(self, user):
        """
        When the user wants to takeback his dislike on a post
        """

        self.disliked_people.remove(user)
        self.power = self.power + 0.2 * user.power

    @property
    def likes(self):
        """
        Returns the number of likes
        """
        return self.liked_people.all().count()

    @property
    def dislikes(self):
        """
        Returns the number of dislikes
        """
        return self.disliked_people.all().count()


class CarouselComment(models.Model):

    """
    A model to store comments - only 1 level of nesting is aloowed, afterwards replies are referred by @username
    """

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=10000)
    liked_people = models.ManyToManyField(User, related_name="liked_comments_carousel")
    disliked_people = models.ManyToManyField(
        User, related_name="disliked_comments_carousel"
    )
    published = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)
    post = models.ForeignKey(
        Carousel, on_delete=models.CASCADE, related_name="comments_carousel"
    )
    reply_to = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, related_name="replies_carousel"
    )  # a comment can be a reply to another comment

    def __str__(self):
        return f"{self.content}"

    def like(self, user):
        self.disliked_people.remove(user)
        self.liked_people.add(user)

    def remove_like(self, user):
        """
        When user wants to takeback his like on a post
        """
        self.liked_people.remove(user)

    def dislike(self, user):
        self.liked_people.remove(user)
        self.disliked_people.add(user)

    def remove_dislike(self, user):
        self.disliked_people.remove(user)

    @property
    def likes(self):
        """
        Returns the number of likes
        """
        return self.liked_people.all().count()

    @property
    def dislikes(self):
        """
        Returns number of dislikes
        """
        return self.disliked_people.all().count()

    @property
    def number_of_replies(self):
        """
        Returns the number of replies
        """

        return self.replies_carousel.all().count()
