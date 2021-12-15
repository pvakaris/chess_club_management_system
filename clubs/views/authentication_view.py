"""Authenticated related views."""
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


@login_prohibited
def log_in(request):
    """View that handles log in."""
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
    """View that handles log out."""
    logout(request)
    return redirect('home')