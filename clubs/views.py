
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from .forms import LogInForm, ApplicationForm, UserForm
from django.contrib.auth.decorators import login_required
from .models import User, Member, Club

def home(request):
    return render(request, 'home.html')

def feed(request):
    return render(request, 'feed.html')

def log_in(request):
    if request.method == 'POST':
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
    return render(request, 'log_in.html', {'form': form})

def log_out(request):
    logout(request)
    return redirect('home')

def apply(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('feed')
    else:
        form = ApplicationForm()
    return render(request, 'application_form.html', {'form': form})
<<<<<<< HEAD

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

def show_user(request, user_id):

    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return redirect('feed')
    else:
        return render(request, 'show_user.html', {'user': user})
=======

def user_list(request):
    members = Member.objects.filter(user_type=3)
    return render(request, 'user_list.html', {'members': members})

def show_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return redirect('user_list')
    else:
        return render(request, 'show_user.html', {'user': user})

>>>>>>> 6fedc83d4a3b9133167375bd733140cf604b6b1e
