from django.db import models
from .user_types import UserTypes
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from libgravatar import Gravatar

# class User(models.Model):
class User(AbstractUser):   
    """User in a club.""" 
    username = models.EmailField(unique=True, blank=False)
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    bio = models.CharField(max_length=520, blank=True)
    chess_experience = models.IntegerField(default=1,blank=False)
    personal_statement = models.CharField(max_length=10000, blank=False)
    followers = models.ManyToManyField(
        'self', symmetrical=False, related_name='followees'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)
    
    def toggle_follow(self, followee):
        """Toggles whether self follows the given followee."""

        if followee==self:
            return
        if self.is_following(followee):
            self._unfollow(followee)
        else:
            self._follow(followee)

    def _follow(self, user):
        user.followers.add(self)

    def _unfollow(self, user):
        user.followers.remove(self)

    def is_following(self, user):
        """Returns whether self follows the given user."""

        return user in self.followees.all()

    def follower_count(self):
        """Returns the number of followers of self."""

        return self.followers.count()

    def followee_count(self):
        """Returns the number of followees of self."""

        return self.followees.count()
    
    class Meta:
        """Model options."""
        ordering = ['-created_at']


class Club(models.Model):
    """A new club."""
    club_name = models.CharField(max_length=50, blank=False, unique=True)

class Member(models.Model): 
    """Member from a certain club with a user type (applicant, officer, etc.)"""
    user_type = models.IntegerField(choices=UserTypes.choices(), default=UserTypes.APPLICANT)
    current_user = models.ForeignKey(User, on_delete=models.CASCADE)
    club_membership = models.ForeignKey(Club, on_delete=models.CASCADE)

class Post(models.Model):
    """Posts by users in their microblogs."""

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Model options."""

        ordering = ['-created_at']