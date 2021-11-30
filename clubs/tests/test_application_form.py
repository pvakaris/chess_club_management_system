from django.test import TestCase
from django import forms
from clubs.models import User
from clubs.forms import ApplicationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password

class SignUpTestCase(TestCase):

    def setUp(self):
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

    def test_valid_sign_up_form(self):
        form = ApplicationForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = ApplicationForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('username', form.fields)
        email_field = form.fields['username']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        self.assertIn('bio', form.fields)
        self.assertIn('chess_experience', form.fields)
        self.assertIn('personal_statement', form.fields)
        self.assertIn('new_password', form.fields)
        new_password_widget = form.fields['new_password'].widget
        self.assertTrue(isinstance(new_password_widget, forms.PasswordInput))
        self.assertIn('password_confirmation', form.fields)
        password_confirmation_widget = form.fields['password_confirmation'].widget
        self.assertTrue(isinstance(password_confirmation_widget, forms.PasswordInput))

    def test_form_uses_model_validation(self):
        self.form_input['username'] = 'notanemail'
        form = ApplicationForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_uppercase_character(self):
        self.form_input['new_password'] = 'password123'
        self.form_input['password_confirmation'] = 'password123'
        form = ApplicationForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_lower_character(self):
        self.form_input['new_password'] = 'PASSWORD123'
        self.form_input['password_confirmation'] = 'PASSWORD123'
        form = ApplicationForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_number(self):
        self.form_input['new_password'] = 'PasswordABC'
        self.form_input['password_confirmation'] = 'PasswordABC'
        form = ApplicationForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_new_password_and_password_confirmation_are_identical(self):
        self.form_input['password_confirmation'] = 'wrongpassword'
        form = ApplicationForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = ApplicationForm(data=self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(before_count+1, after_count)
        user = User.objects.get(username='johndoe@example.org')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.bio, 'This is a bio')
        self.assertEqual(user.chess_experience, 300)
        self.assertEqual(user.personal_statement, 'This is a statement')
        is_password_true = check_password('Password123', user.password)
        self.assertTrue(is_password_true)
