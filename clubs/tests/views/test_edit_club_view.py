from django.urls import reverse
from django.test import TestCase
from clubs.forms import ClubProfileEditingForm
from clubs.models import User, Member, Club
from clubs.user_types import UserTypes

class EditClubViewTestCase(TestCase):

    fixtures = [
        'clubs/tests/fixtures/user.json',
        'clubs/tests/fixtures/other_user.json',
        'clubs/tests/fixtures/club.json'
        ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe@example.org')
        self.other_user = User.objects.get(username='janedoe@example.org')
        self.club = Club.objects.get(name="Club")
        self.url = reverse('edit_club', kwargs={'club_id': self.club.id})
        self.ownership = Member.objects.create(
            user_type=UserTypes.CLUB_OWNER,
            current_user=self.other_user,
            club_membership=self.club
        )
        self.membership = Member.objects.create(
            user_type=UserTypes.MEMBER,
            current_user=self.user,
            club_membership=self.club
        )
        self.form_input = {
            'name': 'New Club',
            'description': 'New Description',
            'location': 'New Location'
        }

    def test_edit_club_url(self):
        self.assertEqual(self.url, f'/edit_club/{self.club.id}')

    def test_get_edit_club(self):
        self.client.login(username=self.other_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_club.html')

    def test_get_edit_club_without_login(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = '/?next=' + self.url
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    def test_get_edit_club_without_club_owner(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_club', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_club.html')

    def test_successful_edit_club(self):
        self.client.login(username=self.other_user.username, password='Password123')
        response = self.client.post(self.url, self.form_input, follow=True)
        redirect_url = reverse('feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')

    def test_unsuccessful_edit_club_blank_name(self):
        self.client.login(username=self.other_user.username, password='Password123')
        self.form_input['name'] = ''
        response = self.client.post(self.url, self.form_input)
        redirect_url = reverse('edit_club', kwargs={'club_id': self.club.id})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ClubProfileEditingForm))
        self.assertTrue(form.is_bound)

    def test_unsuccessful_edit_club_blank_description(self):
        self.client.login(username=self.other_user.username, password='Password123')
        self.form_input['description'] = ''
        response = self.client.post(self.url, self.form_input)
        redirect_url = reverse('edit_club', kwargs={'club_id': self.club.id})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ClubProfileEditingForm))
        self.assertTrue(form.is_bound)

    def test_unsuccessful_edit_club_blank_location(self):
        self.client.login(username=self.other_user.username, password='Password123')
        self.form_input['location'] = ''
        response = self.client.post(self.url, self.form_input)
        redirect_url = reverse('edit_club', kwargs={'club_id': self.club.id})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ClubProfileEditingForm))
        self.assertTrue(form.is_bound)
