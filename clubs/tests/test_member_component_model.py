from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
import clubs.user_types
from clubs.models import *

class MemberModelTestcase(TestCase):
    """Component test for member, club and user since it needs the other two."""
    def setUp(self):
        self.user = User.objects.create_user(
            username='johndoe@example.org',
            first_name='John',
            last_name='Doe',
            password='Password123',
            bio='The quick brown fox jumps over the lazy dog.',
            personal_statement='hhhh',
            chess_experience=101,
        )
        self.club = Club.objects.create(
            name="Club",
            location="Location",
            description="Description"
        )
        self.member = Member.objects.create(
            user_type=UserTypes.APPLICANT,
            current_user=self.user,
            club_membership=self.club
        )

    def test_membership_is_valid(self):
        try:
            self.user.full_clean()
        except (ValidationError):
            self.fail('Test user should be valid')
        try:
            self.club.full_clean()
        except (ValidationError):
            self.fail('Test club should be valid')
        self._assert_membership_is_valid()

    """User type tests"""

    def test_membership_type_may_be_member(self):
        self.member.user_type=UserTypes.MEMBER
        self._assert_membership_is_valid()

    def test_membership_type_may_be_officer(self):
        self.member.user_type=UserTypes.OFFICER
        self._assert_membership_is_valid()

    def test_membership_type_may_be_club_owner(self):
        self.member.user_type=UserTypes.CLUB_OWNER
        self._assert_membership_is_valid()

    def test_membership_type_may_not_be_greater_than_4(self):
        self.member.user_type=5
        self._assert_membership_is_invalid()

    def test_membership_type_may_not_be_less_than_1(self):
        self.member.user_type=0
        self._assert_membership_is_invalid()

    def test_user_type_may_already_exist(self):
        second_user = self._create_second_user()
        second_club = self._create_second_club()
        second_membership = self._create_second_member(second_user, second_club)
        self.member.user_type = second_membership.user_type
        self._assert_membership_is_valid()

    """Current user tests"""

    def test_current_user_may_not_be_null(self):
        self.member.current_user = None
        self._assert_membership_is_invalid()

    def test_current_user_may_already_have_another_membership(self):
        second_club = self._create_second_club()
        second_membership = self._create_second_member(self.user, second_club)
        self._assert_membership_is_valid()

    def test_current_user_cannot_be_a_member_of_same_club_twice(self):
        with self.assertRaises(IntegrityError):
            second_membership = self._create_second_member(self.user, self.club)

    """Club membership tests"""

    def test_club_membership_may_be_the_same_for_different_users(self):
        second_user = self._create_second_user()
        second_membership = self._create_second_member(second_user, self.club)
        self._assert_membership_is_valid()

    def test_club_membership_cannot_be_null(self):
        self.member.club_membership = None
        self._assert_membership_is_invalid()

    """Extra functions"""

    def _assert_membership_is_valid(self):
        try:
            self.member.full_clean()
        except (ValidationError):
            self.fail('Test member should be valid')

    def _assert_membership_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.member.full_clean()

    def _create_second_member(self, otherUser, otherClub):
        second_member = Member.objects.create(
            user_type=UserTypes.MEMBER,
            current_user=otherUser,
            club_membership=otherClub
        )
        return second_member

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

    def _create_second_club(self):
        second_club = Club.objects.create(
            name = "Club2",
            location = "Location2",
            description = "Description2"
        )
        return second_club
