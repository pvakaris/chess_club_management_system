"""Views of the chess club app"""
from logging import exception
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from .forms import LogInForm, SignUpForm, UserProfileEditingForm, ClubApplicationForm, ClubProfileEditingForm, ClubCreationForm, PasswordChangingForm
from django.contrib.auth.decorators import login_required
from .models import User, Member, Club
from .helpers import login_prohibited
from .user_types import UserTypes
from django.http import HttpResponseForbidden, Http404, HttpResponseRedirect
from django.utils.decorators import method_decorator
from system.settings import REDIRECT_URL_WHEN_LOGGED_IN
from django.views import View
from django.urls import reverse
from django.db.models import Q

@login_prohibited
def home(request):
    form = LogInForm()
    return render(request, 'home.html', {'form': form})

@login_required
def feed(request):
    user = request.user
    members = Member.objects.filter(current_user = user)
    return render(request, 'feed.html', {'user': user, 'members': members, 'clubsCount': members.count()})

@login_prohibited
def log_in(request):
    form = LogInForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('feed')
    messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
    form = LogInForm()
    return render(request, 'home.html', {'form': form})

@login_required
def log_out(request):
    logout(request)
    return redirect('home')

@login_required
def password(request):
    current_user = request.user
    if request.method == 'POST':
        form = PasswordChangingForm(data=request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            if check_password(password, current_user.password):
                new_password = form.cleaned_data.get('new_password')
                current_user.set_password(new_password)
                current_user.save()
                login(request, current_user)
                messages.add_message(request, messages.SUCCESS, "Password updated!")
                return redirect('feed')
    form = PasswordChangingForm()
    return render(request, 'password.html', {'form': form})

@login_prohibited
def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('feed')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})

@login_required
def edit_profile(request):
    current_user = request.user
    if request.method == 'POST':
        form = UserProfileEditingForm(instance=current_user, data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Profile updated!")
            form.save()
            return redirect('feed')
    else:
        form = UserProfileEditingForm(instance=current_user)
    return render(request, 'edit_profile.html', {'form': form})

@login_required
def edit_club(request, club_id):
    club = Club.objects.get(id = club_id)
    if request.method == 'POST':
        form = ClubProfileEditingForm(instance=club, data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Club details updated!")
            form.save()
            return redirect('feed')
    else:
        form = ClubProfileEditingForm(instance=club)
    return render(request, 'edit_club.html', {'form': form})

@login_required
def show_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return redirect('member_list')
    else:
        return render(request, 'show_user.html', {'user': user})

@login_required
def show_club(request, club_id):
    try:
        club = Club.objects.get(id=club_id)
    except ObjectDoesNotExist:
        return redirect('club_list')
    else:
        user = request.user
        # To restric users that are not applicants from seeing the club memebr list.
        try:
            user_membership = Member.objects.get(current_user = user, club_membership = club)
            user_type = user_membership.user_type
        except ObjectDoesNotExist: # User is given APPLICANT status even if he is not even an applicant. Restrics from accessing the club memeber list.
            user_type = UserTypes.APPLICANT


        if user_type == UserTypes.MEMBER:
            return render(request, 'show_club.html', {'club': club, 'can_manage_applicants': False, 'is_owner': False, 'is_member': True})
        elif user_type == UserTypes.OFFICER:
            return render(request, 'show_club.html', {'club': club, 'can_manage_applicants': True, 'is_owner': False, 'is_member': True})
        elif user_type == UserTypes.CLUB_OWNER:
            return render(request, 'show_club.html', {'club': club, 'can_manage_applicants': True, 'is_owner': True, 'is_member': True})
        else:
            return render(request, 'show_club.html', {'club': club, 'can_manage_applicants': False, 'is_owner': False, 'is_member': False})

@login_required
def apply(request):
    user = request.user
    if request.method == 'POST':
        form = ClubApplicationForm(request.POST)
        if form.is_valid():
            clubName = form.cleaned_data.get('club')
            club = Club.objects.get(name = clubName)
            try:
                membership = Member.objects.get(current_user=user, club_membership = club)
            except ObjectDoesNotExist:
                Member.objects.create(
                    club_membership = club,
                    current_user = user,
                    user_type = UserTypes.APPLICANT
                )
                messages.add_message(request, messages.SUCCESS, "Application was sent to the club owner!")
            finally:
                return redirect('feed')
        else:
            return redirect('feed')
    else:
        form = ClubApplicationForm()
    return render(request, 'apply.html', {'form': form})


@login_required
def create_club(request):
    user = request.user
    if request.method == 'POST':
        form = ClubCreationForm(request.POST)
        if form.is_valid():
            club = form.save()
            Member.objects.create(
                user_type=UserTypes.CLUB_OWNER,
                current_user=user,
                club_membership=club
            )
            messages.add_message(request, messages.SUCCESS, "Club was created successfully!")
        return redirect('feed')
    else:
        form = ClubCreationForm()
    return render(request, 'create_club.html', {'form': form})

@login_required
def club_members(request, club_id):
    user = request.user
    club = Club.objects.get(id = club_id)
    members = Member.objects.filter(
        Q(user_type = UserTypes.MEMBER, club_membership=club) |
        Q(user_type = UserTypes.OFFICER, club_membership=club) |
        Q(user_type = UserTypes.CLUB_OWNER, club_membership=club)
    )
    # We check if this is the club owner that wants to look at the club members list. If it is, we provide a functionality to promote or kick out members.
    user_membership = Member.objects.get(current_user = user, club_membership = club)
    user_type = user_membership.user_type

    if user_type == UserTypes.CLUB_OWNER:
        return render(request, 'club_member_list.html', {'members' : members, 'club': club, 'is_owner': True, 'request_user_id': user.id})
    else:
        return render(request, 'club_member_list.html', {'members' : members, 'club': club, 'is_owner': False, 'request_user_id': user.id})

@login_required
def manage_applicants(request, club_id):
    club = Club.objects.get(id = club_id)
    applicants = Member.objects.filter(club_membership=club, user_type=UserTypes.APPLICANT)
    return render(request, 'manage_applicants.html', {'applicants': applicants, 'club': club, 'applicants_count': applicants.count()})

@login_required
def manage_officers(request, club_id):
    club = Club.objects.get(id = club_id)
    officers = Member.objects.filter(club_membership=club, user_type=UserTypes.OFFICER)
    return render(request, 'manage_officers.html', {'officers' : officers, 'club' : club, 'officers_count': officers.count()})

##########   PROMOTING MEMBERS, ACCEPTING APPLICATIONS, ETC.   ##########

@login_required
def promote_member(request, club_id, user_id):
    club = Club.objects.get(id = club_id)
    user = User.objects.get(id = user_id)
    # To make sure that only the owner can promote a member
    request_user = request.user
    request_user_membership = Member.objects.filter(club_membership=club, current_user=request_user)
    if request_user_membership == UserTypes.CLUB_OWNER:
        Member.objects.filter(club_membership=club, current_user=user).delete()
        Member.objects.create(
            user_type=UserTypes.OFFICER,
            current_user=user,
            club_membership=club
        )
        messages.add_message(request, messages.SUCCESS, "Member was promoted successfully!")
        return redirect('club_members', club_id)
    else:
        return redirect('feed')

@login_required
def kickout_member(request, club_id, user_id):
    club = Club.objects.get(id = club_id)
    # To make sure that only the owner can kick-out a member
    request_user = request.user
    request_user_membership = Member.objects.filter(club_membership=club, current_user=request_user)
    if request_user_membership == UserTypes.CLUB_OWNER:
        user = User.objects.get(id = user_id)
        Member.objects.filter(club_membership=club, current_user=user).delete()
        messages.add_message(request, messages.SUCCESS, "Member was removed from the club!")
        return redirect('club_members', club_id)
    else:
        return redirect('feed')

@login_required
def demote_officer(request, club_id, user_id):
    club = Club.objects.get(id = club_id)
    # To make sure that only the owner can demote an officer
    request_user = request.user
    request_user_membership = Member.objects.filter(club_membership=club, current_user=request_user)
    if request_user_membership == UserTypes.CLUB_OWNER:
        user = User.objects.get(id = user_id)
        Member.objects.filter(club_membership=club, current_user=user).delete()
        Member.objects.create(
            user_type=UserTypes.MEMBER,
            current_user=user,
            club_membership=club
        )
        messages.add_message(request, messages.SUCCESS, "Officer was demoted!")
        return redirect('manage_officers', club_id)
    else:
        return redirect('feed')

@login_required
def accept_application(request, club_id, user_id):
    club = Club.objects.get(id = club_id)
    # To make sure that only staff members can accept applications
    request_user = request.user
    request_user_membership = Member.objects.filter(club_membership=club, current_user=request_user)
    if request_user_membership == UserTypes.CLUB_OWNER or request_user_membership == UserTypes.OFFICER:
        user = User.objects.get(id = user_id)
        Member.objects.filter(club_membership=club, current_user=user).delete()
        Member.objects.create(
            user_type=UserTypes.MEMBER,
            current_user=user,
            club_membership=club
        )
        messages.add_message(request, messages.SUCCESS, "Application accepted!")
        return redirect('manage_applicants', club_id)
    else:
        return redirect('feed')

@login_required
def decline_application(request, club_id, user_id):
    club = Club.objects.get(id = club_id)
    # To make sure that only staff members can decline applications
    request_user = request.user
    request_user_membership = Member.objects.filter(club_membership=club, current_user=request_user)
    if request_user_membership == UserTypes.CLUB_OWNER or request_user_membership == UserTypes.OFFICER:
        user = User.objects.get(id = user_id)
        Member.objects.filter(club_membership=club, current_user=user).delete()
        messages.add_message(request, messages.WARNING, "Application declined!")
        return redirect('manage_applicants', club_id)
    else:
        return redirect('feed')

@login_required
def make_owner(request, club_id, user_id):
    club = Club.objects.get(id = club_id)
    user = User.objects.get(id = user_id)
    # To make sure that only the owner can reassign his ownership
    request_user = request.user
    request_user_membership = Member.objects.filter(club_membership=club, current_user=request_user)
    if request_user_membership == UserTypes.CLUB_OWNER:
        Member.objects.filter(club_membership=club, current_user=request_user).delete()
        Member.objects.filter(club_membership=club, current_user=user).delete()

        Member.objects.create(
            user_type=UserTypes.CLUB_OWNER,
            current_user=user,
            club_membership=club
        )
        Member.objects.create(
            user_type=UserTypes.MEMBER,
            current_user=request_user,
            club_membership=club
        )
        messages.add_message(request, messages.SUCCESS, "Club ownership was reassigned!")
        return redirect('show_club', club_id)
    else:
        return redirect('feed')

##########   PROMOTING MEMBERS, ACCEPTING APPLICATIONS, ETC.   ##########

class ClubListView(LoginRequiredMixin, ListView):
    """View that shows a list of all clubs."""

    model = Club
    template_name = "club_list.html"
    context_object_name = "clubs"
    paginate_by = settings.CLUBS_PER_PAGE

    def get_queryset(self):
        return Club.objects.all()

class MemberListView(LoginRequiredMixin, ListView):
    """ View that shows a list of all members. """

    model = Member
    template_name = "member_list.html"
    context_object_name = "members"
    paginate_by = settings.MEMBERS_PER_PAGE

    def get_queryset(self):
        # We filter out all the users that are not APPLICANTS (user_type 4).
        members = Member.objects.filter(
            Q(user_type = UserTypes.CLUB_OWNER) |
            Q(user_type = UserTypes.OFFICER) |
            Q(user_type = UserTypes.MEMBER)
        ).order_by('current_user__first_name')
        return members

#class ClubMemberListView(LoginRequiredMixin, ListView):
#    """View that shows a list of all members in the currently selected club"""
#
#    model = Member
#    template_name = "user_list.html"
#    context_object_name = "members"
#    paginate_by = settings.CLUBS_PER_PAGE
#
#
#
#    def get_queryset(self):
#        club = Club.objects.get(id=???)
#        return Member.objects.filter(club_membership=club)
