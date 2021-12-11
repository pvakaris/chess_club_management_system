from django.db import connections, models
from django.db.models.fields import DateTimeField
from django.db.models import CheckConstraint, Q, F
from .user_types import UserTypes
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from libgravatar import Gravatar

class User(AbstractUser):
    """User in a club."""
    username = models.EmailField(unique=True, blank=False, default="")
    first_name = models.CharField(max_length=50, blank=False, default="")
    last_name = models.CharField(max_length=50, blank=False, default="")
    bio = models.CharField(max_length=520, blank=True, default="")
    chess_experience = models.IntegerField(blank=False, validators = [MinValueValidator(0)], default=0)
    personal_statement = models.CharField(max_length=10000, blank=False, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Model options."""
        ordering = ['-created_at']

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


class Club(models.Model):
    """A new club."""
    name = models.CharField(max_length=50, blank=False, unique=True)
    location = models.CharField(max_length=50, blank=False)
    description = models.CharField(max_length=500, blank=False)


class Member(models.Model):
    """Member from a certain club with a user type (applicant, officer, etc.)"""
    user_type = models.IntegerField(choices=UserTypes.choices(), 
                                    default=UserTypes.APPLICANT,
                                    validators=[
                                        MinValueValidator(1),
                                        MaxValueValidator(4)
                                    ]
                                    )
    current_user = models.ForeignKey(User, on_delete=models.CASCADE)
    club_membership = models.ForeignKey(Club, on_delete=models.CASCADE)

    class Meta:
        """Model options."""
        unique_together = ('current_user', 'club_membership')
        constraints = [
            models.UniqueConstraint(fields=['club_membership'], condition=Q(user_type=UserTypes.CLUB_OWNER), name="there can't exist more than one club owner")
        ]


    def acceptApplicant(self, user):
        """Converts an applicant to a member"""
        user.user_type = UserTypes.MEMBER

    def promoteMember(self, user):
        """Converts an member to an officer"""
        user.user_type = UserTypes.OFFICER

    def transferOwnership(self, officer, club_owner):
        """Converts an member to an officer"""
        club_owner.user_type = UserTypes.OFFICER
        officer.user_type = UserTypes.CLUB_OWNER

    def demoteOfficer(self, user):
        """Converts an member to an officer"""
        user.user_type = UserTypes.MEMBER

class Post(models.Model):
    """Posts by users in their microblogs."""

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)
    club_member = models.ForeignKey(Club, on_delete=models.CASCADE)

    class Meta:
        """Model options."""

        ordering = ['-created_at']
