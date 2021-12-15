"""Authenticated related views."""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from clubs.forms import LogInForm
from django.contrib.auth.decorators import login_required
from clubs.helpers import login_prohibited

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