from django.db import models
from .user_types import UserTypes

from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from libgravatar import Gravatar

# class User(models.Model):
class User(AbstractUser):   
    """User in a club."""
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    bio = models.CharField(max_length=520, blank=True)
    chess_experience = models.IntegerField(blank=False)
    personal_statement = models.CharField(max_length=10000, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'bio', 'chess_experience', 'personal_statement']

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
