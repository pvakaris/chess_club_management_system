from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.forms import PasswordChangingForm
from clubs.models import User
from clubs.tests.helpers import LogInTester

class PasswordViewTestCase(TestCase, LogInTester):

    fixtures = ['clubs/tests/fixtures/user.json']

    def setUp(self):
        self.url = reverse('password')
        self.user = User.objects.get(username='johndoe@example.org')
        self.form_input = {
            'password': 'Password123',
            'new_password': 'Password321',
            'password_confirmation': 'Password321'
        }

    def test_password_change_url(self):
        self.assertEqual(self.url, '/password/')

    def test_get_password_change(self):
        self.client.login(username='johndoe@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordChangingForm))
        self.assertFalse(form.is_bound)

    def test_unsuccessful_password_change(self):
        self.client.login(username='johndoe@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        self.assertTrue(check_password('Password123', self.user.password))
        self.form_input['password'] = 'Password111'
        response = self.client.post(self.url, self.form_input)
        passwordafter = self.user.password
        self.assertTrue(check_password('Password123', self.user.password))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordChangingForm))
        self.assertFalse(form.is_bound)

    def test_successful_password_change(self):
        self.client.login(username='johndoe@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        self.assertTrue(check_password('Password123', self.user.password))
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('feed')
        user = User.objects.get(username='johndoe@example.org')
        self.assertTrue(check_password('Password321', user.password))
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')
