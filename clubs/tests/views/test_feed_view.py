from django.test import TestCase
from django.urls import reverse
from clubs.forms import ClubForm
from clubs.models import User, Member, Club
from clubs.user_types import UserTypes
from clubs.tests.helpers import LogInTester

class FeedViewTestCase(TestCase):

    fixtures = ['clubs/tests/fixtures/user.json']

    def setUp(self):
        self.url = reverse('feed', kwargs={'club_id': 0})
        self.user = User.objects.get(username='johndoe@example.org')

    def test_feed_url(self):
        self.assertEqual(self.url, '/feed/0')

    def test_get_feed(self):
        response = self.client.get(self.url, follow=True)
