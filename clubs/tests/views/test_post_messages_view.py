"""Test of the post messages view."""

from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from clubs.forms import PostForm
from clubs.models import User,Member,Club,Post
from clubs.user_types import UserTypes
from clubs.tests.helpers import LogInTester

class PostMessagesViewTestCase(TestCase, LogInTester):
    """Tests of the post messages view"""

    fixtures = ['clubs/tests/fixtures/user.json',
        'clubs/tests/fixtures/other_user.json',
        'clubs/tests/fixtures/club.json',
        'clubs/tests/fixtures/other_club.json']

    def setUp(self):
        self.data = { 'message': 'The quick brown fox jumps over the lazy dog.' }
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
        self.url = reverse('post_messages', kwargs={'club_id': self.club.id})

    def test_post_messages_url(self):
        self.assertEqual(self.url, f'/post_messages/{self.club.id}')

    
    def test_get_post_messages_without_login(self):
        post_count_before = Post.objects.count()
        response = self.client.get(self.url, follow=True)
        post_count_after = Post.objects.count()
        self.assertEqual(post_count_before, post_count_after)
        redirect_url = '/?next=' + self.url
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    def test_successful_post_messages(self):
        self.client.login(username=self.owner.username, password="Password123")
        user_count_before = Post.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        user_count_after = Post.objects.count()
        self.assertEqual(user_count_after, user_count_before+1)
        new_post = Post.objects.latest('created_at')
        self.assertEqual(self.owner, new_post.author)
        response_url = reverse('feed')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'feed.html')
    
    def test_unsuccessful_new_post(self):
        self.client.login(username=self.owner.username, password='Password123')
        user_count_before = Post.objects.count()
        self.data['message'] = ""
        response = self.client.post(self.url, self.data, follow=True)
        user_count_after = Post.objects.count()
        self.assertEqual(user_count_after, user_count_before)
        self.assertTemplateUsed(response, 'post_messages.html')

    def test_post_messages_without_owner_permission(self):
        self.client.login(username=self.officer.username, password='Password123')
        officer_count_before = Post.objects.count()
        response = self.client.get(self.url, follow=True)
        officer_count_after = Post.objects.count()
        self.assertEqual(officer_count_before, officer_count_after)
        redirect_url = reverse('show_club', kwargs={'club_id':f'{self.club.id}'})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_club.html')

    
    