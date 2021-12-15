from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from clubs.models import *
# Create your tests here.


class PostModelTestCase(TestCase):
    """Unit test for the Post model"""

    fixtures = [
        'clubs/tests/fixtures/user.json',
        'clubs/tests/fixtures/other_user.json',
        'clubs/tests/fixtures/club.json',
        'clubs/tests/fixtures/other_club.json'
        ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe@example.org')
        self.club = Club.objects.get(name="Club")
        self.post = Post.objects.create(
            author=self.user,
            club_own=self.club,
            message="1",
        )

    def test_post_is_valid(self):
        try:
            self.user.full_clean()
        except (ValidationError):
            self.fail('Test user should be valid')
        try:
            self.club.full_clean()
        except (ValidationError):
            self.fail('Test club should be valid')
        self._assert_post_is_valid()

    """message tests"""

    def test_message_cannot_be_blank(self):
        self.post.message = ''
        self._assert_post_is_invalid()

    def test_message_may_already_exist(self):
        second_user = User.objects.get(username="janedoe@example.org")
        second_club = Club.objects.get(name="Club2")
        second_post = self._create_second_post(second_user, second_club)
        self.post.message = second_post.message
        self._assert_post_is_valid()

    def test_message_must_be_under_520_characters(self):
        self.post.message = 'x' * 521
        self._assert_post_is_invalid()

    def test_message_may_be_520_characters(self):
        self.post.message = 'x' * 520
        self._assert_post_is_valid()

    """Author tests"""

    def test_author_may_not_be_null(self):
        self.post.author = None
        self._assert_post_is_invalid()

    def test_author_may_already_have_another_post(self):
        second_club = Club.objects.get(name="Club2")
        second_post = self._create_second_post(self.user, second_club)
        self._assert_post_is_valid()

    """Club_own tests"""

    def test_club_own_may_be_the_same_for_different_users(self):
        second_user = User.objects.get(username="janedoe@example.org")
        second_post = self._create_second_post(second_user, self.club)
        self._assert_post_is_valid()

    def test_club_own_cannot_be_null(self):
        self.post.club_own = None
        self._assert_post_is_invalid()

    """Extra functions"""

    def _assert_post_is_valid(self):
        try:
            self.post.full_clean()
        except (ValidationError):
            self.fail('Test post should be valid')

    def _assert_post_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.post.full_clean()

    def _create_second_post(self, otherUser, otherClub):
        second_post = Post.objects.create(
            message="2",
            author=otherUser,
            club_own=otherClub
        )
        return second_post