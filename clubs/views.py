"""Views of the chess club app"""
from logging import exception
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from .forms import LogInForm, SignUpForm, UserForm, ApplicationForm, ClubForm
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

def log_out(request):
    logout(request)
    return redirect('home')

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

def edit_profile(request):
    current_user = request.user
    if request.method == 'POST':
        form = UserForm(instance=current_user, data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Profile updated!")
            form.save()
            return redirect('feed')
    else:
        form = UserForm(instance=current_user)
    return render(request, 'edit_profile.html', {'form': form})

def edit_club(request, club_id):
    club = Club.objects.get(id = club_id)
    if request.method == 'POST':
        form = ClubForm(instance=club, data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Club details updated!")
            form.save()
            return redirect('feed')
    else:
        form = ClubForm(instance=club)
    return render(request, 'edit_club.html', {'form': form})

def show_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return redirect('user_list')
    else:
        return render(request, 'show_user.html', {'user': user})

def show_club(request, club_id):
    try:
        club = Club.objects.get(id=club_id)
    except ObjectDoesNotExist:
        return redirect('club_list')
    else:
        user = request.user
        user_membership = Member.objects.get(current_user = user, club_membership = club)
        user_type = user_membership.user_type
        if user_type == 2:
            return render(request, 'show_club.html', {'club': club, 'can_manage_applicants': True, 'is_owner': False})
        elif user_type == 1:
            return render(request, 'show_club.html', {'club': club, 'can_manage_applicants': True, 'is_owner': True})
        else:
            return render(request, 'show_club.html', {'club': club, 'can_manage_applicants': False, 'is_owner': False})

def apply(request):
    user = request.user
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            clubName = form.cleaned_data.get('club')
            club = Club.objects.get(name = clubName)
            try:
                membership = Member.objects.get(current_user=user, club_membership = club)
            except ObjectDoesNotExist:
                Member.objects.create(
                    club_membership = club,
                    current_user = user,
                    user_type = 4
                )
            finally:
                return redirect('feed')
    else:
        form = ApplicationForm()
    return render(request, 'apply.html', {'form': form})



def create_club(request):
    if request.user.is_authenticated:
        current_usr = request.user
        form = ClubForm(request.POST)
        if form.is_valid():
            club = form.save()
            Member.objects.create(
                user_type=UserTypes.CLUB_OWNER,
                current_user=current_usr,
                club_membership=club
            )
            return redirect('feed')
        else:
            return render(request, 'create_club.html', {'form': form})
    else:
        return HttpResponseRedirect(reverse('home'))

def club_members(request, club_id):
    club = Club.objects.get(id = club_id)
    members = Member.objects.filter(
        Q(user_type = 3, club_membership=club) |
        Q(user_type = 2, club_membership=club) |
        Q(user_type = 1, club_membership=club)
    )
    return render(request, 'club_member_list.html', {'members' : members})

def manage_applicants(request, club_id):
    club = Club.objects.get(id = club_id)
    members = Member.objects.filter(club_membership=club, user_type=4)
    return render(request, 'manage_applicants.html', {'members' : members, 'club_id' : club_id})

def manage_officers(request, club_id):
    club = Club.objects.get(id = club_id)
    members = Member.objects.filter(club_membership=club, user_type=2)
    return render(request, 'manage_applicants.html', {'members' : members, 'club_id' : club_id})

##########   PROMOTING MEMBERS AND ACCEPTING APPLICATIONS   ##########

def promote_member(request, club_id, user_id):
    club = Club.objects.get(id = club_id)
    user = Club.objects.get(id = user_id)
    membership = Member.objects.get(club_membership=club, current_user=user)
    membership.user_type = 2
    return redirect('manage_officers')

def demote_officer(request, club_id, user_id):
    club = Club.objects.get(id = club_id)
    user = Club.objects.get(id = user_id)
    membership = Member.objects.get(club_membership=club, current_user=user)
    membership.user_type = 3
    return redirect('manage_officers')

def accept_application(request, club_id, user_id):
    club = Club.objects.get(id = club_id)
    user = Club.objects.get(id = user_id)
    membership = Member.objects.get(club_membership=club, current_user=user)
    membership.user_type = 2
    return redirect('manage_applicants')

def decline_application(request, club_id, user_id):
    club = Club.objects.get(id = club_id)
    user = Club.objects.get(id = user_id)
    Member.objects.filter(club_membership=club, current_user=user).delete()
    return redirect('manage_applicants')

##########   PROMOTING MEMBERS AND ACCEPTING APPLICATIONS   ##########

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
    template_name = "user_list.html"
    context_object_name = "members"
    paginate_by = settings.MEMBERS_PER_PAGE

    def get_queryset(self):
        # We filter out all the users that are not APPLICANTS (user_type 4).
        members = Member.objects.filter(
            Q(user_type = 3) |
            Q(user_type = 2) |
            Q(user_type = 1)
        )
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
