from django.test import TestCase
from django import forms
from clubs.models import Post
from clubs.forms import PostForm
from django.core.exceptions import ValidationError

class PostFormTestCase(TestCase):

    def setUp(self):
        self.form_input = {
            'message': 'New Post',
        }

    def test_valid_post_form(self):
        form = PostForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = PostForm()
        self.assertIn('message', form.fields)

    def test_form_rejects_blank_message(self):
        self.form_input['message'] = ''
        form = PostForm(data=self.form_input)
        self.assertFalse(form.is_valid())
