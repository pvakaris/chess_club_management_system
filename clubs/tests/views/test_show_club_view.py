from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, Member
from clubs.tests.helpers import reverse_with_next
from clubs.user_types import UserTypes


class ShowClubViewTest(TestCase):
    fixtures = [
        'clubs/tests/fixtures/user.json',
        'clubs/tests/fixtures/club.json',
        'clubs/tests/fixtures/other_user.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe@example.org')
        self.other_user = User.objects.get(username='janedoe@example.org')
        self.club = Club.objects.get(name='Club')
        self.url = reverse('show_club', kwargs={'club_id': self.club.id})
        self.member = Member.objects.create(
            user_type = UserTypes.CLUB_OWNER,
            current_user=self.user,
            club_membership=self.club,
        )

    def test_club_member_url(self):
        self.assertEqual(self.url,f'/club/{self.club.id}')
    
    def test_get_show_club_with_invalid_id(self):
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('show_club', kwargs={'club_id': self.club.id+9999})
        response = self.client.get(url, follow=True)
        response_url = reverse('club_list')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club_list.html')

    def test_get_show_club_with_valid_id(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_club.html')
        self.assertContains(response, "Club")
        self.assertContains(response, "John Doe")
        self.assertContains(response, "johndoe@example.org")
        self.client.login(username=self.other_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_club.html')
        self.assertContains(response, "Club")
        self.assertContains(response, "John Doe")
        self.assertContains(response, "johndoe@example.org")



    def test_get_user_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('home', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

