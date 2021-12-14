from django.test import TestCase
from django import forms
from clubs.models import User
from clubs.forms import PasswordChangingForm
from django.core.exceptions import ValidationError

class PasswordChangingTestCase(TestCase):

    def setUp(self):
        self.form_input = {
            'password': 'Password123',
            'new_password': 'Password321',
            'password_confirmation': 'Password321'
        }

    def test_valid_password_change_form(self):
        form = PasswordChangingForm()
        self.assertIn('password', form.fields)
        current_password_widget = form.fields['password'].widget
        self.assertTrue(isinstance(current_password_widget, forms.PasswordInput))
        self.assertIn('new_password', form.fields)
        new_password_widget = form.fields['new_password'].widget
        self.assertTrue(isinstance(new_password_widget, forms.PasswordInput))
        self.assertIn('password_confirmation', form.fields)
        password_confirmation_widget = form.fields['password_confirmation'].widget
        self.assertTrue(isinstance(password_confirmation_widget, forms.PasswordInput))

    def test_form_must_have_uppercase_characters(self):
        self.form_input['new_password'] = 'password123'
        self.form_input['password_confirmation'] = 'password123'
        form = PasswordChangingForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_have_lowercase_characters(self):
        self.form_input['new_password'] = 'PASSWORD123'
        self.form_input['password_confirmation'] = 'PASSWORD123'
        form = PasswordChangingForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_have_uppercase_characters(self):
        self.form_input['new_password'] = 'password123'
        self.form_input['password_confirmation'] = 'password123'
        form = PasswordChangingForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_number(self):
        self.form_input['new_password'] = 'PasswordABC'
        self.form_input['password_confirmation'] = 'PasswordABC'
        form = PasswordChangingForm(data=self.form_input)
        self.assertFalse(form.is_valid())
