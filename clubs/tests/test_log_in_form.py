from django.test import TestCase
from django import forms
from clubs.models import User
from clubs.forms import LogInForm
from django.core.exceptions import ValidationError

class LogInTestCase(TestCase):
    def setUp(self):
        self.form_input = {
            'username': 'johndoe@example.org',
            'password': 'Password123'
        }

    def test_valid_sign_up_form(self):
        form = LogInForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = LogInForm()
        self.assertIn('username', form.fields)
        email_field = form.fields['username']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        self.assertIn('password', form.fields)
        password_widget = form.fields['password'].widget
        self.assertTrue(isinstance(password_widget, forms.PasswordInput))

    def test_form_rejects_none_email(self):
        self.form_input['username'] = 'janedoe'
        form = LogInForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_email(self):
        self.form_input['username'] = ''
        form = LogInForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_password(self):
        self.form_input['password'] = ''
        form = LogInForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_accepts_incorrect_email(self):
        self.form_input['username'] = 'janedoe@example.org'
        form = LogInForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_accepts_incorrect_password(self):
        self.form_input['password'] = '123password'
        form = LogInForm(data=self.form_input)
        self.assertTrue(form.is_valid())
