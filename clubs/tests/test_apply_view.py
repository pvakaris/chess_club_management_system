from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.forms import ApplicationForm
from clubs.models import User


class ApplicationViewTestCase(TestCase):

    def setUp(self):
        self.url = reverse('application_form')
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

    def test_application_url(self):
        self.assertEqual(reverse('application_form'), '/apply/')

    def test_get_application(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'application_form.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ApplicationForm))
        self.assertFalse(form.is_bound)

    def test_unsuccessful_application(self):
        self.form_input['username'] = 'Not_an_email@'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(before_count, after_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'application_form.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ApplicationForm))
        self.assertTrue(form.is_bound)

    def test_successful_application(self):
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
