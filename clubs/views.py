
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from .forms import LogInForm, SignUpForm, UserForm, ApplicationForm
from django.contrib.auth.decorators import login_required
from .models import User, Member, Club
from .helpers import login_prohibited

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
        form = UserForm(instance=current_user, data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Profile updated!")
            form.save()
            return redirect('feed')
    else:
        form = UserForm(instance=current_user)
    return render(request, 'edit_profile.html', {'form': form})

@login_required
def user_list(request):
    members = Member.objects.filter(user_type=3)
    return render(request, 'user_list.html', {'members': members})

@login_required
def show_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return redirect('user_list')
    else:
        return render(request, 'show_user.html', {'user': user})

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
                return redirect('feed')
    else:
        form = ApplicationForm()
    return render(request, 'apply.html', {'form': form})
