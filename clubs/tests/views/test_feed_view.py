from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Member, Club
from clubs.user_types import UserTypes
from clubs.tests.helpers import LogInTester

class FeedViewTestCase(TestCase):

    fixtures = [
        'clubs/tests/fixtures/user.json',
        'clubs/tests/fixtures/other_user.json',
        'clubs/tests/fixtures/club.json',
        'clubs/tests/fixtures/other_club.json'
    ]

    def setUp(self):
        self.url = reverse('feed')
        self.user = User.objects.get(username='johndoe@example.org')
        self.club = Club.objects.get(name='Club')

    def test_feed_url(self):
        self.assertEqual(self.url, '/feed/')

    def test_get_feed_for_applicant_shows_nothing(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feed.html')

    def test_get_feed_results_in_an_error_when_not_logged_in(self):
        redirect_url = '/?next=' + reverse('feed')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_feed_for_member_shows_clubs(self):
        self.member = Member.objects.create(
            user_type=UserTypes.MEMBER,
            current_user=self.user,
            club_membership=self.club
        )
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feed.html')
        self.assertContains(response, 'Club')
