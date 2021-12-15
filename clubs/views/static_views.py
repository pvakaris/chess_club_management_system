"""Static views of the clubs app."""
from clubs.forms import LogInForm
from clubs.helpers import login_prohibited
from django.shortcuts import render

@login_prohibited
def home(request):
    form = LogInForm()
    return render(request, 'home.html', {'form': form})