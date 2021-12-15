from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, Member
from clubs.tests.helpers import reverse_with_next
from clubs.user_types import UserTypes
from django.conf import settings


class ClubMembersViewTest(TestCase):
    fixtures = [
        'clubs/tests/fixtures/user.json',
        'clubs/tests/fixtures/club.json',
        'clubs/tests/fixtures/other_user.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe@example.org')
        self.other_user = User.objects.get(username='janedoe@example.org')
        self.club = Club.objects.get(name='Club')
        self.url = reverse('club_members', kwargs={'club_id': self.club.id})
        self.member = Member.objects.create(
            user_type = UserTypes.CLUB_OWNER,
            current_user=self.user,
            club_membership=self.club,
        )

    def test_club_member_url(self):
        self.assertEqual(self.url,f'/members/{self.club.id}')

    def test_redirects_when_not_member_of_club(self):
        self.client.login(username=self.other_user.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_club', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_when_applicant_of_club(self):        
        self.client.login(username=self.other_user.username, password='Password123')
        Member.objects.create(
            user_type = UserTypes.APPLICANT,
            current_user=self.other_user,
            club_membership=self.club,
        )
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_club', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_user_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('home', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_club_members_with_invalid_id(self):
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('club_members', kwargs={'club_id': self.club.id+9999})
        response = self.client.get(url, follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')

    def test_get_member_list(self):
        self._create_test_users_and_memberships(settings.MEMBERS_PER_PAGE-1)
        self.client.login(username='johndoe@example.org', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_member_list.html')
        self.assertEqual(len(response.context['members']), settings.MEMBERS_PER_PAGE)
        for user_id in range(settings.MEMBERS_PER_PAGE-1):
            self.assertContains(response, f'user{user_id}@test.org')
            self.assertContains(response, f'First{user_id}')
            self.assertContains(response, f'Last{user_id}')
            user = User.objects.get(username=f'user{user_id}@test.org')
            user_url = reverse('club_member', kwargs={'user_id': user.id, 'club_id': self.club.id})
            self.assertContains(response, user_url)

    def _create_test_users_and_memberships(self, user_count=10):
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

    def test_get_user_list_as_staff(self):
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('club_member', kwargs={'club_id': self.club.id, 'user_id': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user_full.html')
        self.assertContains(response, "John Doe")

        self.client.login(username=self.user.username, password='Password123')
        Member.objects.create(
            user_type = UserTypes.OFFICER,
            current_user=self.other_user,
            club_membership=self.club,
        )
        url = reverse('club_member', kwargs={'club_id': self.club.id, 'user_id': self.other_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user_full.html')
        self.assertContains(response, "Jane Doe")

#TODO test_get_club_members_as_member
#* as member
#* as club owner
#* as officer
