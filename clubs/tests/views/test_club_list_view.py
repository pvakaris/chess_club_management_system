from django.urls import reverse
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from clubs.models import User, Member, Club
from clubs.user_types import UserTypes
from django.conf import settings

class ClubListViewTestCase(TestCase):
    fixtures = ['clubs/tests/fixtures/user.json']

    def setUp(self):
        self.url = reverse('club_list')
        self.user = User.objects.get(username='johndoe@example.org')

    def test_club_list_url(self):
        self.assertEqual(self.url, '/clubs/')

    def test_get_club_list(self):
        self._create_clubs_and_assign_to_user(settings.CLUBS_PER_PAGE)
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_list.html')
        self.assertEqual(len(response.context['clubs']), settings.CLUBS_PER_PAGE)
        for club_id in range(settings.CLUBS_PER_PAGE):
            self.assertContains(response, f'Club{club_id}')
            club = Club.objects.get(name=f'Club{club_id}')
            club_url = reverse('show_club', kwargs={'club_id': club.id})
            self.assertContains(response, club_url)

    def test_get_club_list_with_pagination(self):
        self.client.login(username=self.user.username, password='Password123')
        self._create_clubs_and_assign_to_user(settings.CLUBS_PER_PAGE*2+3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_list.html')
        self.assertEqual(len(response.context['clubs']), settings.CLUBS_PER_PAGE)
        self.assertTrue(response.context['is_paginated'])
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_one_url = reverse('club_list') + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_list.html')
        self.assertEqual(len(response.context['clubs']), settings.CLUBS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_two_url = reverse('club_list') + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_list.html')
        self.assertEqual(len(response.context['clubs']), settings.CLUBS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_three_url = reverse('club_list') + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_list.html')
        self.assertEqual(len(response.context['clubs']), 3)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())

    def test_get_club_list_redirects_when_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse_with_next('home', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    def _create_clubs_and_assign_to_user(self, club_count=10):
        for club_id in range(club_count):
            club = Club.objects.create(
                name=f'Club{club_id}',
                description=f'Description{club_id}',
                location=f'Location{club_id}'
            )
        Member.objects.create(
            current_user=self.user,
            user_type=UserTypes.MEMBER,
            club_membership=club
        )
