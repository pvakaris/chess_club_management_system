from django.shortcuts import render, redirect
from django.views.generic import ListView
from .models import User, Member, Club
from django.contrib.auth.mixins import LoginRequiredMixin

from django.core.exceptions import ObjectDoesNotExist


def home(request):
    return render(request, 'home.html')

def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})
   

def show_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return redirect('user_list')
    else:
        return render(request, 'show_user.html', {'user': user})

    
    