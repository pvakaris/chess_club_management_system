from django.urls import reverse
from django.test import TestCase
from clubs.models import User, Member, Club
from clubs.user_types import UserTypes

class ApplyClubViewTestCase(TestCase):

    fixtures = [
        'clubs/tests/fixtures/user.json',
        'clubs/tests/fixtures/other_club.json',
        'clubs/tests/fixtures/club.json'
        ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe@example.org')
        self.club = Club.objects.get(name='Club')
        self.url = reverse('apply_club', kwargs={'club_id': self.club.id})

    def test_apply_club_url(self):
        self.assertEqual(self.url, '/apply_club/1')

    def test_apply_club(self):
        self.client.login(username=self.user.username, password='Password123')
        count_before = Member.objects.count()
        response = self.client.get(self.url, follow=True)
        count_after = Member.objects.count()
        self.assertEqual(count_after, count_before+1)
        redirect_url = reverse('feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')

    def test_apply_club_without_login_redirects(self):
        count_before = Member.objects.count()
        response = self.client.get(self.url, follow=True)
        count_after = Member.objects.count()
        self.assertEqual(count_after, count_before)
        redirect_url = '/?next=' + self.url
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    # def test_apply_club_while_already_being_member(self):
    #     count_before = Member.objects.count()
    #     response = self.client.get(self.url, follow=True)
    #     count_after = Member.objects.count()
    #     self.assertEqual(count_after, count_before)
    #     redirect_url = reverse('feed')
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    #     self.assertTemplateUsed(response, 'feed.html')
