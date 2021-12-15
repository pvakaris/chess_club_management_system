from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, Member
from clubs.tests.helpers import reverse_with_next
from clubs.user_types import UserTypes

class ClubMemberViewTest(TestCase):

    fixtures = [
        'clubs/tests/fixtures/user.json',
        'clubs/tests/fixtures/club.json',
        'clubs/tests/fixtures/other_user.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe@example.org')
        self.target_user = User.objects.get(username='janedoe@example.org')
        self.club = Club.objects.get(name='Club')
        self.url = reverse('club_member', kwargs={'user_id': self.target_user.id, 'club_id': self.club.id})
        self.member = Member.objects.create(
            user_type = UserTypes.CLUB_OWNER,
            current_user=self.target_user,
            club_membership=self.club,
        )

    def test_club_member_url(self):
        self.assertEqual(self.url,f'/club_member/{self.club.id}/{self.target_user.id}')

    def test_redirects_when_not_member_of_club(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_club', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_when_applicant_of_club(self):
        self.client.login(username=self.user.username, password='Password123')
        Member.objects.create(
            user_type = UserTypes.APPLICANT,
            current_user=self.user,
            club_membership=self.club,
        )
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_club', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_user_list_as_staff(self):
        self.client.login(username=self.target_user.username, password='Password123')
        url = reverse('club_member', kwargs={'club_id': self.club.id, 'user_id': self.target_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user_full.html')
        self.assertContains(response, "Jane Doe")
        self.assertContains(response, "janedoe@example.org")

        self.client.login(username=self.user.username, password='Password123')
        Member.objects.create(
            user_type = UserTypes.OFFICER,
            current_user=self.user,
            club_membership=self.club,
        )
        url = reverse('club_member', kwargs={'club_id': self.club.id, 'user_id': self.target_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user_full.html')
        self.assertContains(response, "Jane Doe")
        self.assertContains(response, "janedoe@example.org")

    def test_get_user_list_as_member(self):
        self.client.login(username=self.target_user.username, password='Password123')
        self.member.user_type = UserTypes.MEMBER
        self.member.save()
        url = reverse('club_member', kwargs={'club_id': self.club.id, 'user_id': self.target_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user.html')
        self.assertContains(response, "Jane Doe")
        self.assertContains(response, "janedoe@example.org")

    def test_get_invalid_user_as_member_redirects(self):
        self.client.login(username=self.target_user.username, password='Password123')
        self.member.user_type = UserTypes.MEMBER
        self.member.save()
        url = reverse('club_member', kwargs={'club_id': self.club.id, 'user_id': self.target_user.id+9999})
        response = self.client.get(url, follow=True)
        redirect_url = reverse('feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')

    def test_get_user_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('home', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
