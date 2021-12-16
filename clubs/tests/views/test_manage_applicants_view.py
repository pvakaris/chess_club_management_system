from django.urls import reverse
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from clubs.models import User, Member, Club
from clubs.user_types import UserTypes
from django.conf import settings

class ManageApplicantsViewTestCase(TestCase):
    fixtures = [
        'clubs/tests/fixtures/user.json',
        'clubs/tests/fixtures/other_user.json',
        'clubs/tests/fixtures/club.json'
        ]

    def setUp(self):
        self.user = User.objects.get(username='alexjordan@example.org')
        self.applicant = User.objects.get(username='johndoe@example.org')
        self.owner = User.objects.get(username='janedoe@example.org')
        self.club = Club.objects.get(name='Club')
        self.application = Member.objects.create(
            user_type=UserTypes.APPLICANT,
            current_user=self.applicant,
            club_membership=self.club
        )
        self.application.save()
        self.ownership = Member.objects.create(
            user_type=UserTypes.CLUB_OWNER,
            current_user=self.owner,
            club_membership=self.club
        )
        self.ownership.save()
        self.url = reverse('manage_applicants', kwargs={'club_id':f'{self.club.id}'})

    def test_manage_applicants_url(self):
        self.assertEqual(self.url, '/manage_applicants/1')

    def test_get_manage_applicants(self):
        self.client.login(username=self.owner.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manage_applicants.html')
        self.assertContains(response, 'John Doe')
        self.assertEqual(len(response.context['applicants']), 1)

    def test_get_manage_applicants_without_login(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse_with_next('home', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    def test_get_manage_applicants_without_having_any_membership(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_club', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_club.html')

    def test_get_manage_applicants_of_invalid_club(self):
        self.client.login(username=self.owner.username, password='Password123')
        url = reverse('manage_applicants', kwargs={'club_id': self.club.id+9999})
        response = self.client.get(url, follow=True)
        redirect_url = reverse('feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')
