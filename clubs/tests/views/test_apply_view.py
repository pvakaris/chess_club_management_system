from django.urls import reverse
from django.test import TestCase
from clubs.models import User, Member, Club
from clubs.user_types import UserTypes

class ApplyViewTestCase(TestCase):

    fixtures = [
        'clubs/tests/fixtures/user.json',
        'clubs/tests/fixtures/other_club.json',
        'clubs/tests/fixtures/club.json'
        ]

    def setUp(self):
        self.url = reverse('apply')
        self.user = User.objects.get(username='johndoe@example.org')
        self.club = Club.objects.get(name='Club')

    def test_apply_url(self):
        self.assertEqual(self.url, '/apply/')

    def test_get_apply(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'apply.html')

    def test_get_apply_without_log_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = '/?next=' + self.url
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    # def test_apply_while_already_registered(self):
    #     self.client.login(username=self.other_user.username, password='Password123')
    #     response = self.client.get(self.url, follow=True)
    #     redirect_url = '/?next=' + self.url
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    #     self.assertTemplateUsed(response, 'apply.html')

    def test_apply_displays_clubs(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'apply.html')
        self.assertEqual(len(response.context['clubs']), 5)
