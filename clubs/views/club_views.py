"""Club related views"""
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
from clubs.forms import LogInForm, SignUpForm, UserProfileEditingForm, ClubProfileEditingForm, ClubCreationForm, PasswordChangingForm, PostForm
from django.contrib.auth.decorators import login_required
from clubs.models import User, Member, Club,Post
from clubs.helpers import login_prohibited, club_owner_required, member_required, staff_required
from clubs.user_types import UserTypes
from django.http import HttpResponseForbidden, Http404, HttpResponseRedirect
from django.utils.decorators import method_decorator
from system.settings import REDIRECT_URL_WHEN_LOGGED_IN
from django.views import View
from django.urls import reverse
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage,InvalidPage


@login_required
def show_club(request, club_id):
    """View that shows individual club details."""
    try:
        club = Club.objects.get(id=club_id)
        club_members = Member.objects.filter(club_membership=club).count()
        posts = Post.objects.filter(club_own_id=club_id).order_by('id')
    except ObjectDoesNotExist:
        return redirect('club_list')
    else:
        user = request.user
        myclubs = Member.objects.filter(current_user = user)
        user_type = None
        try:
            user_membership = Member.objects.get(current_user = user, club_membership = club)
            user_type = user_membership.user_type
        except ObjectDoesNotExist:
            pass
        club_owner = Member.objects.get(Q(user_type = UserTypes.CLUB_OWNER, club_membership=club))
        user = club_owner.current_user
        return render(request, 'show_club.html', {'club': club, 'user_type': user_type, 'user':user, 'club_members': club_members, 'myclubs': myclubs, 'posts':posts})


@login_required
def create_club(request):
    """View that creates club."""
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
        return redirect('create_club')
    else:
        form = ClubCreationForm()
    return render(request, 'create_club.html', {'form': form, 'myclubs': members})


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

@login_required
def apply(request):
    """View that shows all clubs your not a member of"""
    user = request.user
    members = Member.objects.filter(current_user = user)
    clubset = set()
    clubs = Club.objects.all()
    for club in clubs:
        try:
            Member.objects.get(current_user=user, club_membership=club)
        except ObjectDoesNotExist:
            clubset.add(club)
    return render(request, 'apply.html', {'clubs': clubset, 'myclubs':members})