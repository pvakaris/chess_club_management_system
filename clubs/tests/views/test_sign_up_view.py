from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.forms import SignUpForm
from clubs.models import User


class SignUpViewTestCase(TestCase):

    fixtures = ['clubs/tests/fixtures/other_user.json']

    def setUp(self):
        self.url = reverse('sign_up')
        self.form_input = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe@example.org',
            'bio': 'This is a bio',
            'chess_experience': 300,
            'personal_statement': 'This is a statement',
            'new_password': 'Password123',
            'password_confirmation': 'Password123'
        }
        self.other_user = User.objects.get(username='janedoe@example.org')

    def test_sign_up_url(self):
        self.assertEqual(self.url, '/sign_up/')

    def test_get_sign_up(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertFalse(form.is_bound)

    def test_get_sign_up_when_logged_in(self):
        self.client.login(username=self.other_user.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')

    def test_unsuccessful_sign_up(self):
        self.form_input['username'] = 'Not_an_email@'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(before_count, after_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertTrue(form.is_bound)

    def test_successful_sign_up(self):
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(before_count+1, after_count)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')
        user = User.objects.get(username='johndoe@example.org')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.bio, 'This is a bio')
        self.assertEqual(user.chess_experience, 300)
        self.assertEqual(user.personal_statement, 'This is a statement')
        is_password_true = check_password('Password123', user.password)
        self.assertTrue(is_password_true)
