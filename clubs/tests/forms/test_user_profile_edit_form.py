from django.test import TestCase
from django import forms
from clubs.models import User
from clubs.forms import UserProfileEditingForm
from django.core.exceptions import ValidationError



class UserProfileEditingTestCase(TestCase):

    def setUp(self):
        self.form_input = {
            'first_name': 'Jonathan',
            'last_name': 'Doremi',
            'username': 'jonadore@example.org',
            'bio': 'updated bio',
            'chess_experience': 1000,
            'personal_statement': 'My new statement'
        }

    def test_valid_user_edit_form(self):
        form = UserProfileEditingForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = UserProfileEditingForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('username', form.fields)
        email_field = form.fields['username']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        self.assertIn('bio', form.fields)
        self.assertIn('chess_experience', form.fields)
        self.assertIn('personal_statement', form.fields)

    def test_form_rejects_blank_first_name(self):
        self.form_input['first_name'] = ''
        form = UserProfileEditingForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_last_name(self):
        self.form_input['last_name'] = ''
        form = UserProfileEditingForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_username(self):
        self.form_input['username'] = ''
        form = UserProfileEditingForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_accepts_blank_bio(self):
        self.form_input['bio'] = ''
        form = UserProfileEditingForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_null_chess_experience(self):
        self.form_input['chess_experience'] = None
        form = UserProfileEditingForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_personal_statement(self):
        self.form_input['personal_statement'] = ''
        form = UserProfileEditingForm(data=self.form_input)
        self.assertFalse(form.is_valid())
