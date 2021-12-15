from django.test import TestCase
from django import forms
from clubs.models import Club
from clubs.forms import ClubCreationForm
from django.core.exceptions import ValidationError

class ClubCreationTestCase(TestCase):

    def setUp(self):
        self.form_input = {
            'name': 'New Club',
            'location': 'New Location',
            'description': 'New description'
        }

    def test_valid_club_creation_form(self):
        form = ClubCreationForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = ClubCreationForm()
        self.assertIn('name', form.fields)
        self.assertIn('location', form.fields)
        self.assertIn('description', form.fields)

    def test_form_rejects_blank_name(self):
        self.form_input['name'] = ''
        form = ClubCreationForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_location(self):
        self.form_input['location'] = ''
        form = ClubCreationForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_description(self):
        self.form_input['description'] = ''
        form = ClubCreationForm(data=self.form_input)
        self.assertFalse(form.is_valid())
