from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import User
# Create your tests here.


class UserModelTestCase(TestCase):
    """Unit test for the User model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='johndoe@example.org',
            first_name='John',
            last_name='Doe',
            password='password123',
            bio='The quick brown fox jumps over the lazy dog.',
            personal_statement='hhhh',
            chess_experience=101,
        )

    def test_valid_user(self):
        self._assert_user_is_valid()


    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except (ValidationError):
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()