"""Account related views."""
from logging import exception
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.generic import ListView, FormView
from django.views.generic.edit import FormView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.urls import reverse
import logging
from clubs.forms import PasswordChangingForm, UserProfileEditingForm, SignUpForm, ClubProfileEditingForm
from django.contrib.auth.decorators import login_required
from clubs.models import User, Member, Club,Post
from clubs.helpers import login_prohibited, club_owner_required
from .mixins import LoginProhibitedMixin

@login_required
def password(request):
    """View to handle password change requests."""
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

@login_required
def edit_profile(request):
    """View to update logged-in user's profile."""
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
    
class SignUpView(LoginProhibitedMixin, FormView):
    """View that signs up user."""

    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)

@login_required
@club_owner_required
def edit_club(request, club_id):
    """View to update club profile."""
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