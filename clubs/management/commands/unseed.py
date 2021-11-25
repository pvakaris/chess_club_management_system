from django.core.management.base import BaseCommand, CommandError
from clubs.models import User, Member, Club

# ! modify

class Command(BaseCommand):
    def handle(self, *args, **options):
        Member.objects.all().delete()
        User.objects.filter(is_staff=False, is_superuser=False).delete()
        Club.objects.all().delete()
