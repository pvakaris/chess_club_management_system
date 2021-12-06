from django.urls import reverse
from django.test import TestCase
from clubs.models import User
from .helpers import LogInTester

class LogInViewTestCase(TestCase, LogInTester):

    def setUp(self):
        self.url = reverse('log_out')
        self.user = User.objects.create_user(
            username='johndoe@example.org',
            first_name='John',
            last_name='Doe',
            password='Password123',
            bio='The quick brown fox jumps over the lazy dog.',
            personal_statement='hhhh',
            chess_experience=101,
        )

    def test_log_out_url(self):
        self.assertEqual(self.url, '/log_out/')

    def test_get_log_out(self):
        self.client.login(username='johndoe@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertFalse(self._is_logged_in())
