from django.urls import reverse
from django.test import TestCase
from clubs.models import User, Member, Club
from clubs.user_types import UserTypes

class TestMakeOwnerViewTestCase(TestCase):

    fixtures = [
        'clubs/tests/fixtures/user.json',
        'clubs/tests/fixtures/other_user.json',
        'clubs/tests/fixtures/club.json',
        'clubs/tests/fixtures/other_club.json'
    ]

    def setUp(self):
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
        self.url = reverse('make_owner', kwargs={
            'club_id': f'{self.club.id}',
            'user_id': f'{self.officer.id}'
        })

    def test_make_owner_url(self):
        self.assertEqual(self.url, f'/make_owner/{self.club.id}/{self.officer.id}')

    def test_successful_make_owner(self):
        self.client.login(username=self.owner.username, password='Password123')
        officer_count_before = Member.objects.filter(user_type=UserTypes.OFFICER).count()
        response = self.client.get(self.url, follow=True)
        officer_count_after = Member.objects.filter(user_type=UserTypes.OFFICER).count()
        self.assertEqual(officer_count_before, officer_count_after)
        redirect_url = reverse('show_club', kwargs={'club_id':f'{self.club.id}'})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_club.html')

    def test_get_make_owner_without_login(self):
        officer_count_before = Member.objects.filter(user_type=UserTypes.OFFICER).count()
        response = self.client.get(self.url, follow=True)
        officer_count_after = Member.objects.filter(user_type=UserTypes.OFFICER).count()
        self.assertEqual(officer_count_before, officer_count_after)
        redirect_url = '/?next=' + self.url
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    def test_make_owner_without_owner_permission_fails(self):
        self.client.login(username=self.officer.username, password='Password123')
        officer_count_before = Member.objects.filter(user_type=UserTypes.OFFICER).count()
        response = self.client.get(self.url, follow=True)
        officer_count_after = Member.objects.filter(user_type=UserTypes.OFFICER).count()
        self.assertEqual(officer_count_before, officer_count_after)
        redirect_url = reverse('show_club', kwargs={'club_id':f'{self.club.id}'})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_club.html')
