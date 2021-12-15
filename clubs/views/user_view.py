"""User related views."""
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
def show_user(request, user_id):
    """View that shows individual user details."""
    current_user = request.user
    members = Member.objects.filter(current_user = current_user)
    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return redirect('member_list')
    else:
        return render(request, 'show_user.html', {'user': user, 'myclubs':members})