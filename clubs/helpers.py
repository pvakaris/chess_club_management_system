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

def club_owner_required(view_function):
    def modified_view_function(request, club_id, user_id=None):
        user = request.user
        club = Club.objects.get(id=club_id)
        try:
            member = Member.objects.get(current_user=user, club_membership=club)
            if member.user_type == UserTypes.CLUB_OWNER:
                if user_id:
                    return view_function(request, club_id, user_id)
                else:
                    return view_function(request, club_id)
            else:
                return redirect('show_club', club_id)
        except ObjectDoesNotExist:
            return redirect(settings.REDIRECT_WEN_NOT_CLUB_OWNER)
    return modified_view_function

