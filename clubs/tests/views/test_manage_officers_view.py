from django.urls import reverse
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from clubs.models import User, Member, Club
from clubs.user_types import UserTypes
from django.conf import settings

class ManageOfficersViewTestCase(TestCase):
    fixtures = [
        'clubs/tests/fixtures/user.json',
        'clubs/tests/fixtures/other_user.json',
        'clubs/tests/fixtures/club.json'
        ]

    def setUp(self):
        self.officer = User.objects.get(username='johndoe@example.org')
        self.owner = User.objects.get(username='janedoe@example.org')
        self.club = Club.objects.get(name='Club')
        self.office = Member.objects.create(
            user_type=UserTypes.OFFICER,
            current_user=self.officer,
            club_membership=self.club
        )
        self.office.save()
        self.ownership = Member.objects.create(
            user_type=UserTypes.CLUB_OWNER,
            current_user=self.owner,
            club_membership=self.club
        )
        self.ownership.save()
        self.url = reverse('manage_officers', kwargs={'club_id':f'{self.club.id}'})

    def test_manage_officers_url(self):
        self.assertEqual(self.url, '/manage_officers/1')

    def test_get_manage_officers(self):
        self.client.login(username=self.owner.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manage_officers.html')
        self.assertContains(response, 'John Doe')
        self.assertEqual(len(response.context['officers']), 1)

    def test_get_manage_officers_without_login(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse_with_next('home', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

# pagination?
