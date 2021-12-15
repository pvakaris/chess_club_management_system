from django.urls import reverse
from django.test import TestCase
from clubs.models import User, Member, Club
from clubs.user_types import UserTypes

class TestAcceptApplicationViewTestCase(TestCase):

    fixtures = [
        'clubs/tests/fixtures/user.json',
        'clubs/tests/fixtures/other_user.json',
        'clubs/tests/fixtures/club.json',
        'clubs/tests/fixtures/other_club.json'
    ]

    def setUp(self):
        self.applicant = User.objects.get(username='johndoe@example.org')
        self.member = User.objects.get(username='alexjordan@example.org')
        self.owner = User.objects.get(username='janedoe@example.org')
        self.club = Club.objects.get(name='Club')
        self.application = Member.objects.create(
            user_type=UserTypes.APPLICANT,
            current_user=self.applicant,
            club_membership=self.club
        )
        self.application.save()
        self.membership = Member.objects.create(
            user_type=UserTypes.MEMBER,
            current_user=self.member,
            club_membership=self.club
        )
        self.membership.save()
        self.ownership = Member.objects.create(
            user_type=UserTypes.CLUB_OWNER,
            current_user=self.owner,
            club_membership=self.club
        )
        self.ownership.save()
        self.url = reverse('accept_application', kwargs={
            'club_id': f'{self.club.id}',
            'user_id': f'{self.applicant.id}'
        })

    def test_accept_application_url(self):
        self.assertEqual(self.url, f'/accept_application/{self.club.id}/{self.applicant.id}')

    def test_successful_accept_application(self):
        self.client.login(username=self.owner.username, password='Password123')
        member_count_before = Member.objects.filter(user_type=UserTypes.MEMBER).count()
        response = self.client.get(self.url, follow=True)
        member_count_after = Member.objects.filter(user_type=UserTypes.MEMBER).count()
        self.assertEqual(member_count_before+1, member_count_after)
        redirect_url = reverse('manage_applicants', kwargs={'club_id':f'{self.club.id}'})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'manage_applicants.html')

    def test_get_accept_application_without_login(self):
        member_count_before = Member.objects.filter(user_type=UserTypes.MEMBER).count()
        response = self.client.get(self.url, follow=True)
        member_count_after = Member.objects.filter(user_type=UserTypes.MEMBER).count()
        self.assertEqual(member_count_before, member_count_after)
        redirect_url = '/?next=' + self.url
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    def test_decline_application_without_staff_permission_fails(self):
        self.client.login(username=self.member.username, password='Password123')
        member_count_before = Member.objects.filter(user_type=UserTypes.MEMBER).count()
        response = self.client.get(self.url, follow=True)
        member_count_after = Member.objects.filter(user_type=UserTypes.MEMBER).count()
        self.assertEqual(member_count_before, member_count_after)
        redirect_url = reverse('show_club', kwargs={'club_id':f'{self.club.id}'})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_club.html')

    def test_get_invalid_id_for_accept_application_redirects(self):
        self.client.login(username=self.owner.username, password='Password123')
        member_count_before = Member.objects.filter(user_type=UserTypes.MEMBER).count()
        self.url = reverse('accept_application', kwargs={
            'club_id': self.club.id,
            'user_id': self.applicant.id+9999
        })
        response = self.client.get(self.url, follow=True)
        member_count_after = Member.objects.filter(user_type=UserTypes.MEMBER).count()
        self.assertEqual(member_count_before, member_count_after)
        redirect_url = reverse('feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')
