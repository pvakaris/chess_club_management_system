from django.conf import settings
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from .models import User, Member, Club
from .user_types import UserTypes
import logging

def login_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)
    return modified_view_function


