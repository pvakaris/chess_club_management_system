from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Post, Member
from clubs.tests.helpers import reverse_with_next

class ShowUserTest(TestCase):

    fixtures = [
        'clubs/tests/fixtures/user.json',
        'clubs/tests/fixtures/other_user.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe@example.org')
        self.target_user = User.objects.get(username='janedoe@example.org')
        self.url = reverse('show_user', kwargs={'user_id': self.target_user.id})

    def test_show_user_url(self):
        self.assertEqual(self.url,f'/user/{self.target_user.id}')

    def test_get_show_user_with_valid_id(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user.html')
        self.assertContains(response, "Jane Doe")
        self.assertContains(response, "janedoe@example.org")

    def test_get_show_user_with_own_id(self):
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user_full.html')
        self.assertContains(response, "John Doe")
        self.assertContains(response, "johndoe@example.org")

    def test_get_show_user_with_invalid_id(self):
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.user.id+9999})
        response = self.client.get(url, follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')

    def test_get_show_user_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('home', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
