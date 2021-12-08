from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import User
# Create your tests here.


class UserModelTestCase(TestCase):
    """Unit test for the User model"""

    fixtures = ['clubs/tests/fixtures/user.json']

    def setUp(self):
        self.user = User.objects.get(username='johndoe@example.org')

    def test_valid_user(self):
        self._assert_user_is_valid()

    """Username tests"""

    def test_email_must_be_unique(self):
        second_user = self._create_second_user()
        self.user.username = second_user.username
        self._assert_user_is_invalid()

    def test_email_must_have_something_before_the_at(self):
        self.user.username = '@domainname.com'
        self._assert_user_is_invalid()

    def test_email_must_have_one_at_symbol(self):
        self.user.username = 'wrongemail@@domainname.com'
        self._assert_user_is_invalid()

    def test_email_must_have_a_domain_name(self):
        self.user.username = 'wrongemail@.com'
        self._assert_user_is_invalid()

    def test_email_may_have_more_than_one_dot(self):
        self.user.username = 'rightemail@domainname.co.uk'
        self._assert_user_is_valid()

    def test_email_must_have_at_least_one_dot(self):
        self.user.username = 'wrongemail@domaincom'
        self._assert_user_is_invalid()

    def test_email_must_have_a_domain(self):
        self.user.username = 'wrongemail@domain.'
        self._assert_user_is_invalid()

    """First name tests"""

    def test_first_name_must_not_be_blank(self):
        self.user.first_name = ''
        self._assert_user_is_invalid()

    def test_first_name_may_already_exist(self):
        second_user = self._create_second_user()
        self.user.first_name = second_user.first_name
        self._assert_user_is_valid()

    def test_first_name_must_have_50_characters_maximum(self):
        self.user.first_name = 'x' * 51
        self._assert_user_is_invalid()

    def test_first_name_can_be_50_characters_long(self):
        self.user.first_name = 'x' * 50
        self._assert_user_is_valid()

    """Last name tests"""

    def test_last_name_must_not_be_blank(self):
        self.user.last_name = ''
        self._assert_user_is_invalid()

    def test_last_name_may_already_exist(self):
        second_user = self._create_second_user()
        self.user.last_name = second_user.last_name
        self._assert_user_is_valid()

    def test_last_name_must_have_50_characters_maximum(self):
        self.user.last_name = 'x' * 51
        self._assert_user_is_invalid()

    def test_last_name_can_be_50_characters_long(self):
        self.user.last_name = 'x' * 50
        self._assert_user_is_valid()

    """Bio tests"""

    def test_bio_may_be_blank(self):
        self.user.bio = ''
        self._assert_user_is_valid()

    def test_bio_may_already_exist(self):
        second_user = self._create_second_user()
        self.user.bio = second_user.bio
        self._assert_user_is_valid()

    def test_bio_must_be_under_520_characters(self):
        self.user.bio = 'a' * 521
        self._assert_user_is_invalid()

    def test_bio_may_be_520_characters(self):
        self.user.bio = 'a' * 520
        self._assert_user_is_valid()

    """Personal statement tests"""

    def test_personal_statement_cannot_be_blank(self):
        self.user.personal_statement = ''
        self._assert_user_is_invalid()

    def test_personal_statement_may_already_exist(self):
        second_user = self._create_second_user()
        self.user.personal_statement = second_user.personal_statement
        self._assert_user_is_valid()

    def test_personal_statement_must_be_under_10000_characters(self):
        self.user.personal_statement = 'x' * 10001
        self._assert_user_is_invalid()

    def test_personal_may_be_10000_characters(self):
        self.user.personal_statement = 'x' * 10000
        self._assert_user_is_valid()

    """Chess experience tests"""

    def test_chess_experience_cannot_be_negative(self):
        self.user.chess_experience = -1
        self._assert_user_is_invalid()

    def test_chess_experience_may_already_exist(self):
        second_user = self._create_second_user()
        self.user.chess_experience = second_user.chess_experience
        self._assert_user_is_valid()

    """Extra functions"""

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except (ValidationError):
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def _create_second_user(self):
        second_user = User.objects.create_user(
            username='janedoe@example.org',
            first_name='Jane',
            last_name='Doe',
            password='password123',
            bio='The quick brown fox jumps over the lazy dog.',
            personal_statement='hhhh',
            chess_experience=300,
        )
        return second_user
