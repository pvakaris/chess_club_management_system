from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from clubs.models import User, Member, Club
from clubs.user_types import UserTypes

class MemberListTest(TestCase):
    fixtures = [
        'clubs/tests/fixtures/user.json',
        'clubs/tests/fixtures/other_user.json',
        'clubs/tests/fixtures/club.json',
        'clubs/tests/fixtures/other_club.json'
    ]

    def setUp(self):
        self.url = reverse('member_list')
        self.user = User.objects.get(username='johndoe@example.org')
        self.club = Club.objects.get(name='Club')
        self.member = Member.objects.create(
            user_type=UserTypes.MEMBER,
            current_user=self.user,
            club_membership=self.club
        )

    def test_member_list_url(self):
        self.assertEqual(self.url,'/members/')

    def test_get_member_list(self):
        self._create_test_members_and_memberships(settings.MEMBERS_PER_PAGE-1)
        self.client.login(username='johndoe@example.org', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'member_list.html')
        self.assertEqual(len(response.context['members']), settings.MEMBERS_PER_PAGE)
        for user_id in range(settings.MEMBERS_PER_PAGE-1):
            self.assertContains(response, f'user{user_id}@test.org')
            self.assertContains(response, f'First{user_id}')
            self.assertContains(response, f'Last{user_id}')
            user = User.objects.get(username=f'user{user_id}@test.org')
            user_url = reverse('show_user', kwargs={'user_id': user.id})
            self.assertContains(response, user_url)

    def test_get_member_list_with_pagination(self):
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_members_and_memberships(settings.MEMBERS_PER_PAGE*2+3-1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'member_list.html')
        self.assertEqual(len(response.context['members']), settings.MEMBERS_PER_PAGE)
        self.assertTrue(response.context['is_paginated'])
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_one_url = reverse('member_list') + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'member_list.html')
        self.assertEqual(len(response.context['members']), settings.MEMBERS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_two_url = reverse('member_list') + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'member_list.html')
        self.assertEqual(len(response.context['members']), settings.MEMBERS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_three_url = reverse('member_list') + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'member_list.html')
        self.assertEqual(len(response.context['members']), 3)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())

    def test_get_member_list_redirects_when_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = "/?next=" + self.url
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    def _create_test_members_and_memberships(self, user_count=10):
        for user_id in range(user_count):
            User.objects.create_user(
                username=f'user{user_id}@test.org',
                password='Password123',
                first_name=f'First{user_id}',
                last_name=f'Last{user_id}',
                bio=f'Bio {user_id}',
                chess_experience=user_id,
                personal_statement=f'Statement {user_id}',
            )
            Member.objects.create(
                user_type=UserTypes.MEMBER,
                current_user=User.objects.get(username=f'user{user_id}@test.org'),
                club_membership=self.club
            )
"""Needs to be changed to member list and actual code changed a bit more"""
