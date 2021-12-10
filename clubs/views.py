"""Views of the chess club app"""
from logging import exception
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
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


from .helpers import login_prohibited, SelectedClubTracker

selected_club_tracker = SelectedClubTracker.instance()

@login_prohibited
def home(request):
    form = LogInForm()
    return render(request, 'home.html', {'form': form})


@login_required
def feed(request, club_id):
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
            return redirect('feed', selected_club_tracker.current_club)
    messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
    form = LogInForm()
    return render(request, 'home.html', {'form': form})

@login_required
def log_out(request):
    selected_club_tracker.current_club = 0
    logout(request)
    return redirect('home')

@login_prohibited
def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('feed', selected_club_tracker.current_club)
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})

@login_required
def edit_profile(request):
    current_user = request.user
    if request.method == 'POST':
        form = UserForm(instance=current_user, data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Profile updated!")
            form.save()
            return redirect('feed', selected_club_tracker.current_club)
    else:
        form = UserForm(instance=current_user)
    return render(request, 'edit_profile.html', {'form': form})

@login_required
def edit_club(request):
    current_club = selected_club_tracker.current_club

    if current_club == 0:
        return redirect('feed', selected_club_tracker.current_club)

    club = Club.objects.get(id = current_club)
    if request.method == 'POST':
        form = ClubForm(instance=club, data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Club details updated!")
            form.save()
            return redirect('feed', current_club)
    else:
        form = ClubForm(instance=club)
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
    selected_club_tracker.current_club = club_id
    try:
        club = Club.objects.get(id=club_id)
    except ObjectDoesNotExist:
        return redirect('club_list')
    else:
        return render(request, 'show_club.html', {'club': club})

@login_required
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
                return redirect('feed', selected_club_tracker.current_club)
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
            return redirect('/feed/0')
        else:
            return render(request, 'create_club.html', {'form': form})
    else:
        return HttpResponseRedirect(reverse('home'))

class ClubListView(LoginRequiredMixin, ListView):
    """View that shows a list of all clubs."""

    model = Club
    template_name = "club_list.html"
    context_object_name = "clubs"
    paginate_by = settings.CLUBS_PER_PAGE

    def get_queryset(self):
        return Club.objects.all()

class MemberListView(LoginRequiredMixin, ListView):
    """View that shows a list of all members."""

    model = Member
    template_name = "user_list.html"
    context_object_name = "members"
    paginate_by = settings.MEMBERS_PER_PAGE

    def get_queryset(self):
        return Member.objects.filter(user_type=3)

class ClubMemberListView(LoginRequiredMixin, ListView):
    """View that shows a list of all members in the currently selected club"""

    model = Member
    template_name = "user_list.html"
    context_object_name = "members"
    paginate_by = settings.CLUBS_PER_PAGE

    def get_queryset(self):
        club = Club.objects.get(id=selected_club_tracker.current_club)
        return Member.objects.filter(club_membership=club)
