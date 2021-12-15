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

    def test_get_password_change_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        redirect_url = '/?next=' + self.url
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    def test_unsuccessful_password_change_with_incorrect_current_password(self):
        self.client.login(username='johndoe@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        self.form_input['password'] = 'Password111'
        response = self.client.post(self.url, self.form_input)
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordChangingForm))
        self.user.refresh_from_db()
        self.assertTrue(check_password('Password123', self.user.password))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordChangingForm))
        self.assertFalse(form.is_bound)

    def test_unsuccessful_password_change_with_incorrect_confirmation(self):
        self.client.login(username='johndoe@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        self.form_input['password_confirmation'] = 'Password111'
        response = self.client.post(self.url, self.form_input)
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordChangingForm))
        self.user.refresh_from_db()
        self.assertTrue(check_password('Password123', self.user.password))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordChangingForm))
        self.assertFalse(form.is_bound)

    def test_successful_password_change(self):
        self.client.login(username='johndoe@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('feed')
        self.user.refresh_from_db()
        self.assertTrue(check_password('Password321', self.user.password))
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')
