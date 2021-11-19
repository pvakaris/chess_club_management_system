from django.test import TestCase
from clubs.models import User
from clubs.models import Club
from clubs.models import Member
from clubs.user_types import UserTypes
from django.core.exceptions import ValidationError
# Create your tests here.

class UserModelTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            first_name = 'John',
            last_name = 'Doe',
            email = 'johndoe@example.org',
            bio = 'This is a bio',
            chess_experience = True,
            personal_statement = 'This is a statement'
        )
        self.club = new Club
        self.club

    """The first test to prevent the base Applicant from being invalid"""
    def test_valid_applicant(self):
        self._assert_user_is_valid()

    """The start of the main tests"""


    """Assertions"""
    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except (ValidationError):
            self.self.fail('User is invalid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()
