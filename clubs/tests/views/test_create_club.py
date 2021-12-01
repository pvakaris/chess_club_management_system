"""Test of the create club view."""

from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from clubs.forms import ClubForm
from clubs.models import User, Member, Club
from clubs.user_types import UserTypes
from clubs.tests.helpers import LogInTester



class CreateClubTestCase(TestCase):
    """Tests of the create club view"""

    def setUp(self):
        super(TestCase, self).setUp()
        self.url = reverse('create_club')
        self.club = {
            'name': 'KCL chess',
            'location': 'London',
            'description': 'KCL chess club is the leading chess club in london'
        }
        self.user = User.objects.create_user(
            username='johndoe@example.org',
            first_name='John',
            last_name='Doe',
            password='Password123',
            bio='My bio',
            personal_statement='My statement',
            chess_experience=101,
            is_active=True,
        )
        self.other_user = User.objects.create_user(
            username='janedoe@example.org',
            first_name='Jane',
            last_name='Doe',
            password='Password123',
            bio='The quick brown fox jumps over the lazy dog.',
            personal_statement='hhhh',
            chess_experience=101,
            is_active=True,
        )

    def test_create_club_url(self):
        self.assertEqual(self.url, '/create_club/')
    
    def test_get_create_club_is_forbidden(self): #? needed
        pass

    def test_create_club_redirects_when_not_logged_in(self): #! later stage
        pass

    def test_successfull_create_club(self):
        self.client.login(username=self.user.username, password="Password123")
        club_count_before = Club.objects.count()
        members_count_before = Member.objects.count()
        user_count_before = User.objects.count()
        response = self.client.post(self.url, self.club, follow=True)
        club_count_after = Club.objects.count()
        members_count_after = Member.objects.count()
        user_count_after= User.objects.count()
        self.assertEqual(club_count_after, club_count_before+1)
        self.assertEqual(members_count_after, members_count_before+1)
        self.assertEqual(user_count_after, user_count_before)
        KCL_club = Club.objects.get(name='KCL chess')
        KCL_members = Member.objects.filter(club_membership=KCL_club).count()
        self.assertEqual(KCL_members, 1)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')
        club = Club.objects.get(name='KCL chess')
        self.assertEqual(club.location, 'London')
        self.assertEqual(club.description, 'KCL chess club is the leading chess club in london')

    def test_unsuccessful_create_club_no_name(self):
        self.client.login(username=self.user.username, password='Password123')
        user_count_before = Club.objects.count()
        self.club['name'] = ""
        response = self.client.post(self.url, self.club, follow=True)
        user_count_after = Club.objects.count()
        self.assertEqual(user_count_after, user_count_before)
        self.assertTemplateUsed(response, 'create_club.html')

    def test_unsuccessful_create_club_no_location(self):
        self.client.login(username=self.user.username, password='Password123')
        user_count_before = Club.objects.count()
        self.club['location'] = ""
        response = self.client.post(self.url, self.club, follow=True)
        user_count_after = Club.objects.count()
        self.assertEqual(user_count_after, user_count_before)
        self.assertTemplateUsed(response, 'create_club.html')

    def test_unsuccessful_create_club_no_description(self):
        self.client.login(username=self.user.username, password='Password123')
        user_count_before = Club.objects.count()
        self.club['description'] = ""
        response = self.client.post(self.url, self.club, follow=True)
        user_count_after = Club.objects.count()
        self.assertEqual(user_count_after, user_count_before)
        self.assertTemplateUsed(response, 'create_club.html')

    def test_cannot_create_two_equal_club_names(self): #? necessary
        pass
    