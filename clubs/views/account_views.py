"""Account related views."""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth import login
from django.shortcuts import redirect, render
from clubs.forms import PasswordChangingForm, UserProfileEditingForm, SignUpForm, ClubProfileEditingForm
from django.contrib.auth.decorators import login_required
from clubs.models import Member, Club
from clubs.helpers import login_prohibited, club_owner_required

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

@login_prohibited
def sign_up(request):
    """View that signs up user."""
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