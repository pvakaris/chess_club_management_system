from django.urls import reverse
from django.test import TestCase
from clubs.forms import UserProfileEditingForm
from clubs.models import User
from clubs.tests.helpers import LogInTester

class EditProfileViewTestCase(TestCase):

    fixtures = ['clubs/tests/fixtures/user.json']

    def setUp(self):
        self.url = reverse('edit_profile')
        self.user = User.objects.get(username='johndoe@example.org')
        self.form_input = {
            'first_name': 'Jonathan',
            'last_name': 'Doremi',
            'username': 'jonadore@example.org',
            'bio': 'updated bio',
            'chess_experience': 1000,
            'personal_statement': 'My new statement'
        }

    def test_edit_profile_url(self):
        self.assertEqual(self.url, '/edit_profile/')

    def test_get_edit_profile(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')

    def test_get_edit_profile_redirects_when_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = '/?next=' + self.url
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    def test_successful_edit_profile(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.url, self.form_input, follow=True)
        redirect_url = reverse('feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')

    def test_successful_edit_profile_blank_bio(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['bio'] = ''
        response = self.client.post(self.url, self.form_input, follow=True)
        redirect_url = reverse('feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')

    def test_unsuccessful_edit_profile_blank_username(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['username'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserProfileEditingForm))
        self.assertTrue(form.is_bound)

    def test_unsuccessful_edit_profile_blank_first_name(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['first_name'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserProfileEditingForm))
        self.assertTrue(form.is_bound)

    def test_unsuccessful_edit_profile_blank_last_name(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['last_name'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserProfileEditingForm))
        self.assertTrue(form.is_bound)

    def test_unsuccessful_edit_profile_negative_chess_experience(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['chess_experience'] = -1
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserProfileEditingForm))
        self.assertTrue(form.is_bound)

    def test_unsuccessful_edit_profile_blank_personal_statement(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['personal_statement'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserProfileEditingForm))
        self.assertTrue(form.is_bound)
