from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from clubs.models import Club, User, Member
from django.db.utils import IntegrityError
import random
from clubs.user_types import UserTypes

class Command(BaseCommand):
    PASSWORD = "Password123"
    USER_COUNT = 150
    CLUB_COUNT = 5

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.populate_reqired_users()
        
        self.create_users() 
        self.create_clubs()
        self.create_members() 

        print('Seeding complete')
    
    def create_users(self):
        """Populate database with users"""
        user_count = 0
        while user_count < Command.USER_COUNT:
            print(f'Seeding user {user_count}',  end='\r')
            try:
                self._create_user()
            except (IntegrityError):
                continue
            user_count += 1
        print()

    def create_clubs(self):
        """Populate database with clubs"""
        club_count = 0
        while club_count < Command.CLUB_COUNT:
            print(f'Seeding clubs {club_count}',  end='\r')
            try:
                self._create_club()
            except (IntegrityError):
                continue
            club_count += 1
        print()

    def create_members(self):
        """Populate database with members"""
        member_count = 0
        users = list(User.objects.all())
        clubs = list(Club.objects.all())
        while member_count < Command.USER_COUNT:
            print(f'Seeding members {member_count}',  end='\r')
            try:
                rand = random.randint(0,Command.CLUB_COUNT-1)
                self._create_member(users[member_count], clubs[rand])
            except (IntegrityError):
                continue
            member_count += 1
        print()

    def _create_user(self):
        """Create a random user"""
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        username = self._email(first_name, last_name)
        bio = self.faker.text(max_nb_chars=520)
        chess_experience = self.faker.random_int(0, 3000)
        personal_statement = self.faker.text(max_nb_chars=10000)
        User.objects.create_user(
            username,
            first_name=first_name,
            last_name=last_name,
            password=Command.PASSWORD,
            bio=bio,
            chess_experience=chess_experience,
            personal_statement=personal_statement,
        )
    
    def _create_club_owner(self, user, club):
        Member.objects.create(
            user_type = UserTypes.CLUB_OWNER,
            current_user=user,
            club_membership=club,
        )
    
    def _create_member(self, user, club):
        """Create a random member"""
        options = list(map(int ,UserTypes))
        user_type = random.choices(options, cum_weights=(0, 0.2, 0.4, 0.4), k=1)
        Member.objects.create(
            user_type = user_type[0]+1,
            current_user=user,
            club_membership=club,
        )

    def _create_club(self):
        """Create a random club"""
        name = self.faker.domain_word()
        location = self.faker.city()
        description=self.faker.text(max_nb_chars=500)
        Club.objects.create(
            name=name,
            location=location,
            description=description,
        )
        self._create_club_owner(User.objects.order_by('?').first(), Club.objects.get(name=name))


    def _email(self, first_name, last_name):
        email = f'{first_name}.{last_name}@example.org'
        return email

    def _username(self, first_name, last_name):
        username = f'@{first_name}{last_name}'
        return username
    
    def _create_default_user(self, first_name, last_name, email):
        """Create specific user"""
        try:
            User.objects.get(username=email)
        except User.DoesNotExist:
            bio = self.faker.text(max_nb_chars=520)
            chess_experience = self.faker.random_int(0, 3000)
            personal_statement = self.faker.text(max_nb_chars=10000)
            User.objects.create_user(
                username=email,
                first_name=first_name,
                last_name=last_name,
                password=Command.PASSWORD,
                bio=bio,
                chess_experience=chess_experience,
                personal_statement=personal_statement,
            )

    def _create_default_member(self, membership_type, current_user, club_membership):
        """Create specific member"""
        try:
            Member.objects.get(current_user=current_user, club_membership=club_membership)
        except Member.DoesNotExist:
            Member.objects.create(
                user_type = membership_type,
                current_user=current_user,
                club_membership=club_membership,
            )

    def _create_default_club(self, name):
        """Create specific club"""
        try:
            Club.objects.get(name=name)
        except Club.DoesNotExist:
            location = self.faker.city()
            description=self.faker.text(max_nb_chars=500)
            Club.objects.create(
                name = name,
                location = location,
                description = description,
            )
    
    def populate_reqired_users(self):
        """Populate required users"""
        self._create_default_club("Kerbal Chess Club")

        self._create_default_user("Jebediah", "Kerman", "jeb@example.org")    
        self._create_default_user("Valentina", "Kerman", "val@example.org")
        self._create_default_user("Billie", "Kerman", "billie@example.org")
        
        self._create_default_member(3, 
                            User.objects.get(username="jeb@example.org"),
                            Club.objects.get(name="Kerbal Chess Club")
                            )
        
        self._create_default_member(2, 
                            User.objects.get(username="val@example.org"),
                            Club.objects.get(name="Kerbal Chess Club")
                            )

        self._create_default_member(1, 
                            User.objects.get(username="billie@example.org"),
                            Club.objects.get(name="Kerbal Chess Club")
                            )
