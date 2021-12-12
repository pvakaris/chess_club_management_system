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
import logging
from .forms import LogInForm, SignUpForm, UserProfileEditingForm, ClubApplicationForm, ClubProfileEditingForm, ClubCreationForm, PasswordChangingForm
from django.contrib.auth.decorators import login_required
from .models import User, Member, Club
from .helpers import login_prohibited, club_owner_required, member_required, staff_required
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

@login_required #TODO show the amount of club members
def feed(request):
    user = request.user
    members = Member.objects.filter(current_user = user)
    return render(request, 'feed.html', {'user': user, 'myclubs': members})

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
    members = Member.objects.filter(current_user = current_user)
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
        else:
            messages.add_message(request, messages.ERROR, "Please check your input!")                
    form = PasswordChangingForm()
    return render(request, 'password.html', {'form': form, 'myclubs':members})

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
    members = Member.objects.filter(current_user = current_user)
    if request.method == 'POST':
        form = UserProfileEditingForm(instance=current_user, data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Profile updated!")
            form.save()
            return redirect('feed')
    else:
        form = UserProfileEditingForm(instance=current_user)
    return render(request, 'edit_profile.html', {'form': form, 'myclubs':members})


@club_owner_required
@login_required
def edit_club(request, club_id):
    current_user = request.user
    members = Member.objects.filter(current_user = current_user)
    club = Club.objects.get(id = club_id)
    if request.method == 'POST':
        form = ClubProfileEditingForm(instance=club, data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Club details updated!")
            form.save()
            return redirect('feed')
    else:
        form = ClubProfileEditingForm(instance=club)
    return render(request, 'edit_club.html', {'form': form, 'club': club, 'myclubs':members})

@login_required
def show_user(request, user_id):
    current_user = request.user
    members = Member.objects.filter(current_user = current_user)
    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return redirect('member_list')
    else:
        return render(request, 'show_user.html', {'user': user, 'myclubs':members})

@member_required
@login_required
def club_member(request, club_id, user_id):
    """Shows a club member with respect to what membership type you possess."""
    user = User.objects.get(id=user_id)
    club = Club.objects.get(id=club_id)
    current_user = request.user
    members = Member.objects.filter(current_user = current_user)
    member = Member.objects.get(current_user=current_user, club_membership=club)
    if(member.user_type == UserTypes.MEMBER):
        return render(request, 'show_user.html', {'user': user, 'myclubs':members})
    else:
        return render(request, 'show_user_full.html', {'user': user, 'myclubs':members})

@login_required
def show_club(request, club_id): #TODO show club owners profile
    """View to show the bio of a club."""
    try:
        club = Club.objects.get(id=club_id)
    except ObjectDoesNotExist:
        return redirect('club_list')
    else:
        user = request.user
        members = Member.objects.filter(current_user = user)
        user_type = None
        try:
            user_membership = Member.objects.get(current_user = user, club_membership = club)
            user_type = user_membership.user_type
            club_members = Member.objects.filter(club_membership=club).count()
        except ObjectDoesNotExist: 
            pass
        club_owner = Member.objects.get(Q(user_type = UserTypes.CLUB_OWNER, club_membership=club))
        user = club_owner.current_user
        return render(request, 'show_club.html', {'club': club, 'user_type': user_type, 'user':user, 'club_members': club_members, 'myclubs': members})

@login_required
def apply(request):
    """view to apply to a club."""
    user = request.user
    members = Member.objects.filter(current_user = user)
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
    return render(request, 'apply.html', {'form': form, 'myclubs':members})


@login_required
def create_club(request):
    user = request.user
    members = Member.objects.filter(current_user = user)
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
    return render(request, 'create_club.html', {'form': form, 'myclubs': members})

@member_required
@login_required
def club_members(request, club_id):
    user = request.user
    club = Club.objects.get(id = club_id)
    members = Member.objects.filter(
        Q(user_type = UserTypes.MEMBER, club_membership=club) |
        Q(user_type = UserTypes.OFFICER, club_membership=club) |
        Q(user_type = UserTypes.CLUB_OWNER, club_membership=club)
    )
    myClubs = Member.objects.filter(current_user = user)
    user_membership = Member.objects.get(current_user = user, club_membership = club)
    user_type = user_membership.user_type

    if user_type == UserTypes.CLUB_OWNER:
        return render(request, 'club_member_list.html', {'members' : members, 'club': club, 'is_owner': True, 'request_user_id': user.id, 'myclubs':myClubs})
    else:
        return render(request, 'club_member_list.html', {'members' : members, 'club': club, 'is_owner': False, 'request_user_id': user.id, 'myclubs': myClubs})

@staff_required
@login_required
def manage_applicants(request, club_id):
    user = request.user
    myClubs = Member.objects.filter(current_user = user)
    club = Club.objects.get(id = club_id)
    applicants = Member.objects.filter(club_membership=club, user_type=UserTypes.APPLICANT)
    return render(request, 'manage_applicants.html', {'applicants': applicants, 'club': club, 'applicants_count': applicants.count(), 'myclubs':myClubs})

@club_owner_required
@login_required
def manage_officers(request, club_id):
    user = request.user
    myClubs = Member.objects.filter(current_user = user)
    club = Club.objects.get(id = club_id)
    officers = Member.objects.filter(club_membership=club, user_type=UserTypes.OFFICER)
    return render(request, 'manage_officers.html', {'officers' : officers, 'club' : club, 'officers_count': officers.count(), 'myclubs':myClubs})

@staff_required
@login_required
def promote_member(request, club_id, user_id):
    """View that promotes a member to an officer"""
    club = Club.objects.get(id = club_id)
    user = User.objects.get(id = user_id)
    request_user = request.user
    request_user_membership = Member.objects.get(club_membership=club, current_user=request_user)
    if request_user_membership.user_type == UserTypes.CLUB_OWNER:
        Member.promoteMember(user, club)
        messages.add_message(request, messages.SUCCESS, "Member was promoted successfully!")
        return redirect('club_members', club_id)
    else:
        return redirect('feed')

@staff_required
@login_required
def kickout_member(request, club_id, user_id):
    """View that kicks a member out of the current club"""
    club = Club.objects.get(id = club_id)
    request_user = request.user
    request_user_membership = Member.objects.get(club_membership=club, current_user=request_user)
    if request_user_membership.user_type == UserTypes.CLUB_OWNER:
        user = User.objects.get(id = user_id)
        Member.kickOutMember(user, club)
        messages.add_message(request, messages.SUCCESS, "Member was removed from the club!")
        return redirect('club_members', club_id)
    else:
        return redirect('feed')

@club_owner_required
@login_required
def demote_officer(request, club_id, user_id):
    """View to demote an officer to a member"""
    club = Club.objects.get(id = club_id)
    officer_to_demote = User.objects.get(id = user_id)
    current_user = request.user
    current_member = Member.objects.get(club_membership=club, current_user=current_user)
    if current_member.user_type == UserTypes.CLUB_OWNER:
        current_member.demoteOfficer(officer_to_demote, club)
        messages.add_message(request, messages.SUCCESS, "Officer was demoted!")
        return redirect('manage_officers', club_id)
    else:
        return redirect('feed')


@staff_required
@login_required
def accept_application(request, club_id, user_id):
    """View to accept an applicant and make him/her a member"""
    club = Club.objects.get(id = club_id)
    current_user = request.user
    current_member = Member.objects.get(club_membership=club, current_user=current_user)
    if current_member.user_type == UserTypes.CLUB_OWNER or current_member.user_type == UserTypes.OFFICER:
        user = User.objects.get(id = user_id)
        current_member.acceptApplicant(user, club)
        messages.add_message(request, messages.SUCCESS, "Application accepted!")
        return redirect('manage_applicants', club_id)
    else:
        return redirect('feed')

@staff_required
@login_required
def decline_application(request, club_id, user_id):
    """Declines an applicant"""
    club = Club.objects.get(id = club_id)
    request_user = request.user
    request_user_membership = Member.objects.get(club_membership=club, current_user=request_user)
    if request_user_membership.user_type == UserTypes.CLUB_OWNER or request_user_membership.user_type == UserTypes.OFFICER:
        user = User.objects.get(id = user_id)
        Member.objects.filter(club_membership=club, current_user=user).delete()
        messages.add_message(request, messages.WARNING, "Application declined!")
        return redirect('manage_applicants', club_id)
    else:
        return redirect('feed')

@club_owner_required
@login_required
def make_owner(request, club_id, user_id):
    """Transfer ownership to other club member"""
    club = Club.objects.get(id = club_id)
    new_club_owner = User.objects.get(id = user_id)
    old_club_owner = request.user
    request_user_membership = Member.objects.get(club_membership=club, current_user=old_club_owner)
    if request_user_membership.user_type == UserTypes.CLUB_OWNER:
        request_user_membership.transferOwnership(new_club_owner, old_club_owner, club)
        messages.add_message(request, messages.SUCCESS, "Club ownership was reassigned!")
        return redirect('show_club', club_id)
    else:
        return redirect('feed')


class ClubListView(LoginRequiredMixin, ListView):
    """View that shows a list of all clubs."""

    model = Club
    template_name = "club_list.html"
    context_object_name = "clubs"
    paginate_by = settings.CLUBS_PER_PAGE

    def get_queryset(self):
        """Return all clubs."""
        return Club.objects.all()
    
    def get_context_data(self, **kwargs):
        """Return context data, including new post form."""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['myclubs'] = Member.objects.filter(current_user = user)
        return context

class MemberListView(LoginRequiredMixin, ListView):
    """ View that shows a list of all members. """

    model = Member
    template_name = "member_list.html"
    context_object_name = "members"
    paginate_by = settings.MEMBERS_PER_PAGE

    def get_queryset(self):
        members = Member.objects.filter(
            Q(user_type = UserTypes.CLUB_OWNER) |
            Q(user_type = UserTypes.OFFICER) |
            Q(user_type = UserTypes.MEMBER)
        ).order_by('current_user__first_name')
        return members

    def get_context_data(self, **kwargs):
        """Return context data, including new post form."""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['myclubs'] = Member.objects.filter(current_user = user)
        return context

#TODO refactor views.py -> create folder with files
