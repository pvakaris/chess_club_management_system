from django.urls import reverse
from django.test import TestCase
from clubs.models import User, Member, Club
from clubs.user_types import UserTypes

class PromoteMemberViewTestCase(TestCase):

    fixtures = [
        'clubs/tests/fixtures/user.json',
        'clubs/tests/fixtures/other_user.json',
        'clubs/tests/fixtures/club.json',
        'clubs/tests/fixtures/other_club.json'
    ]

    def setUp(self):
        self.member = User.objects.get(username='johndoe@example.org')
        self.officer = User.objects.get(username='alexjordan@example.org')
        self.owner = User.objects.get(username='janedoe@example.org')
        self.club = Club.objects.get(name='Club')
        self.membership = Member.objects.create(
            user_type=UserTypes.MEMBER,
            current_user=self.member,
            club_membership=self.club
        )
        self.membership.save()
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
        self.url = reverse('promote_member', kwargs={
            'club_id': f'{self.club.id}',
            'user_id': f'{self.member.id}'
        })

    def test_promote_member_url(self):
        self.assertEqual(self.url, f'/promote_member/{self.club.id}/{self.member.id}')

    def test_successful_promote_member(self):
        self.client.login(username=self.owner.username, password='Password123')
        member_count_before = Member.objects.filter(user_type=UserTypes.MEMBER).count()
        response = self.client.get(self.url, follow=True)
        member_count_after = Member.objects.filter(user_type=UserTypes.MEMBER).count()
        self.assertEqual(member_count_before, member_count_after+1)
        redirect_url = reverse('club_members', kwargs={'club_id':f'{self.club.id}'})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club_member_list.html')

    def test_get_promote_member_without_login(self):
        member_count_before = Member.objects.filter(user_type=UserTypes.MEMBER).count()
        response = self.client.get(self.url, follow=True)
        member_count_after = Member.objects.filter(user_type=UserTypes.MEMBER).count()
        self.assertEqual(member_count_before, member_count_after)
        redirect_url = '/?next=' + self.url
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    def test_promote_member_without_owner_permission(self):
        self.client.login(username=self.officer.username, password='Password123')
        officer_count_before = Member.objects.filter(user_type=UserTypes.OFFICER).count()
        response = self.client.get(self.url, follow=True)
        officer_count_after = Member.objects.filter(user_type=UserTypes.OFFICER).count()
        self.assertEqual(officer_count_before, officer_count_after)
        redirect_url = reverse('feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')
