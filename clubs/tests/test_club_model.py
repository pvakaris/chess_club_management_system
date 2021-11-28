from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import Club

class ClubModelTestCase(TestCase):
    """Unit tests for club model"""
    def setUp(self):
        self.club = Club.objects.create(
            name = "Club",
            location = "Location",
            description = "Description"
        )

    def test_valid_club(self):
        self._assert_club_is_valid()

    """Name tests"""

    def test_name_must_not_be_blank(self):
        self.club.name = ''
        self._assert_club_is_invalid()

    def test_name_cannot_already_exist(self):
        second_club = self._create_second_club()
        self.club.name = second_club.name
        self._assert_club_is_invalid()

    def test_name_must_have_50_characters_maximum(self):
        self.club.name = 'x' * 51
        self._assert_club_is_invalid()

    def test_name_can_be_50_characters_long(self):
        self.club.name = 'x' * 50
        self._assert_club_is_valid()

    """Location tests"""

    def test_location_may_be_blank(self):
        self.club.location = ''
        self._assert_club_is_valid()

    def test_location_may_already_exist(self):
        second_club = self._create_second_club()
        self.club.location = second_club.location
        self._assert_club_is_valid()

    def test_location_must_be_under_520_characters(self):
        self.club.location = 'a' * 51
        self._assert_club_is_invalid()

    def test_location_may_be_520_characters(self):
        self.club.location = 'a' * 50
        self._assert_club_is_valid()

    """Description tests"""

    def test_description_may_be_blank(self):
        self.club.description = ''
        self._assert_club_is_valid()

    def test_description_may_already_exist(self):
        second_club = self._create_second_club()
        self.club.description = second_club.description
        self._assert_club_is_valid()

    def test_description_must_be_under_500_characters(self):
        self.club.description = 'a' * 501
        self._assert_club_is_invalid()

    def test_description_may_be_500_characters(self):
        self.club.description = 'a' * 500
        self._assert_club_is_valid()

    """Extra functions"""

    def _assert_club_is_valid(self):
        try:
            self.club.full_clean()
        except (ValidationError):
            self.fail('Test club should be valid')

    def _assert_club_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.club.full_clean()

    def _create_second_club(self):
        second_club = Club.objects.create(
            name = "Club2",
            location = "Location2",
            description = "Description2"
        )
        return second_club
