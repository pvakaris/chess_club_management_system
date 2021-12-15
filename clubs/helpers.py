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
        try:
            club = Club.objects.get(id=club_id)
            member = Member.objects.get(current_user=user, club_membership=club)
            if member.user_type == UserTypes.CLUB_OWNER:
                if user_id:
                    return view_function(request, club_id, user_id)
                else:
                    return view_function(request, club_id)
            else:
                return redirect('show_club', club_id)
        except Club.DoesNotExist:
            return redirect('feed') 
        except  Member.DoesNotExist:
            return redirect('show_club', club_id)

    return modified_view_function

def staff_required(view_function):
    def modified_view_function(request, club_id, user_id=None):
        user = request.user
        try:
            club = Club.objects.get(id=club_id)
            member = Member.objects.get(current_user=user, club_membership=club)
            if member.user_type == UserTypes.CLUB_OWNER or member.user_type == UserTypes.OFFICER:
                if user_id:
                    return view_function(request, club_id, user_id)
                else:
                    return view_function(request, club_id)
            else:
                return redirect('show_club', club_id)
        except Club.DoesNotExist:
            return redirect('feed') 
        except  Member.DoesNotExist:
            return redirect('show_club', club_id)  
    return modified_view_function

def member_required(view_function):
    def modified_view_function(request, club_id, user_id=None):
        user = request.user
        try:
            club = Club.objects.get(id=club_id)
            member = Member.objects.get(current_user=user, club_membership=club)
            if member.user_type == UserTypes.CLUB_OWNER or member.user_type == UserTypes.OFFICER or member.user_type == UserTypes.MEMBER:
                if user_id:
                    return view_function(request, club_id, user_id)
                else:
                    return view_function(request, club_id)
            else:
                return redirect('show_club', club_id)
        except Club.DoesNotExist:
            return redirect('feed') 
        except  Member.DoesNotExist:
            return redirect('show_club', club_id)
    return modified_view_function


#TODO retrieve get_users_clubs
#TODO get user_type current user
