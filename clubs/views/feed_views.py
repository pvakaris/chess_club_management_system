"""Feed related views."""
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

@login_required #TODO show the amount of club members
def feed(request):
    """View for displaying a feed."""
    user = request.user
    clubs = Club.objects.filter(
    id__in=Member.objects.filter(
        current_user=user).exclude(user_type = 4).values("club_membership")
    ).values("id")
    posts = Post.objects.filter(club_own_id__in=clubs).order_by('id')
    members = Member.objects.filter(current_user = user)
    paginator = Paginator(posts, 10)
    try:
        page_number = request.GET.get('page', '1')
        page = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage, InvalidPage):
        page = paginator.page(1)

    return render(request, 'feed.html', {'user': user, 'myclubs': members,'page':page})