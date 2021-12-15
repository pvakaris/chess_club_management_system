from django.urls import reverse
from django.test import TestCase
from clubs.models import User, Member, Club
from clubs.user_types import UserTypes

class DemoteOfficerViewTestCase(TestCase):

    fixtures = [
        'clubs/tests/fixtures/user.json',
        'clubs/tests/fixtures/other_user.json',
        'clubs/tests/fixtures/club.json',
        'clubs/tests/fixtures/other_club.json'
    ]

    def setUp(self):
        self.officer = User.objects.get(username='johndoe@example.org')
        self.other_officer = User.objects.get(username='alexjordan@example.org')
        self.owner = User.objects.get(username='janedoe@example.org')
        self.club = Club.objects.get(name='Club')
        self.office = Member.objects.create(
            user_type=UserTypes.OFFICER,
            current_user=self.officer,
            club_membership=self.club
        )
        self.office.save()
        self.other_office = Member.objects.create(
            user_type=UserTypes.OFFICER,
            current_user=self.other_officer,
            club_membership=self.club
        )
        self.other_office.save()
        self.ownership = Member.objects.create(
            user_type=UserTypes.CLUB_OWNER,
            current_user=self.owner,
            club_membership=self.club
        )
        self.ownership.save()
        self.url = reverse('demote_officer', kwargs={
            'club_id': f'{self.club.id}',
            'user_id': f'{self.officer.id}'
        })

    def test_demote_officer_url(self):
        self.assertEqual(self.url, f'/demote_officer/{self.club.id}/{self.officer.id}')

    def test_successful_demote_officer(self):
        self.client.login(username=self.owner.username, password='Password123')
        member_count_before = Member.objects.filter(user_type=UserTypes.MEMBER).count()
        response = self.client.get(self.url, follow=True)
        member_count_after = Member.objects.filter(user_type=UserTypes.MEMBER).count()
        self.assertEqual(member_count_before+1, member_count_after)
        redirect_url = reverse('manage_officers', kwargs={'club_id':f'{self.club.id}'})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'manage_officers.html')

    def test_get_demote_officer_without_login(self):
        member_count_before = Member.objects.filter(user_type=UserTypes.OFFICER).count()
        response = self.client.get(self.url, follow=True)
        member_count_after = Member.objects.filter(user_type=UserTypes.OFFICER).count()
        self.assertEqual(member_count_before, member_count_after)
        redirect_url = '/?next=' + self.url
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    def test_demote_officer_without_owner_permission_fails(self):
        self.client.login(username=self.other_officer.username, password='Password123')
        officer_count_before = Member.objects.filter(user_type=UserTypes.OFFICER).count()
        response = self.client.get(self.url, follow=True)
        officer_count_after = Member.objects.filter(user_type=UserTypes.OFFICER).count()
        self.assertEqual(officer_count_before, officer_count_after)
        redirect_url = reverse('show_club', kwargs={'club_id':f'{self.club.id}'})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_club.html')
