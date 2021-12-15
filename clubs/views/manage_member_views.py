"""Manage member related views"""
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from clubs.models import User, Member, Club
from clubs.helpers import club_owner_required, staff_required
from clubs.user_types import UserTypes
from django.core.exceptions import ObjectDoesNotExist

@login_required
@club_owner_required
def promote_member(request, club_id, user_id):
    """View that promotes a member to an officer"""
    club = Club.objects.get(id = club_id)
    user = User.objects.get(id = user_id)
    Member.promoteMember(user, club)
    messages.add_message(request, messages.SUCCESS, "Member was promoted successfully!")
    return redirect('club_members', club_id)

@login_required
@club_owner_required
def kickout_member(request, club_id, user_id):
    """View that kicks a member out"""
    club = Club.objects.get(id = club_id)
    user = User.objects.get(id = user_id)
    Member.kickOutMember(user, club)
    messages.add_message(request, messages.SUCCESS, "Member was removed from the club!")
    return redirect('club_members', club_id)

@login_required
@club_owner_required
def demote_officer(request, club_id, user_id):
    """View that demote an officer to a member"""
    club = Club.objects.get(id = club_id)
    officer_to_demote = User.objects.get(id = user_id)
    Member.demoteOfficer(officer_to_demote, club)
    messages.add_message(request, messages.SUCCESS, "Officer was demoted!")
    return redirect('manage_officers', club_id)

@login_required
@staff_required
def accept_application(request, club_id, user_id):
    """View that accept an applicant and make member"""
    club = Club.objects.get(id = club_id)
    user = User.objects.get(id = user_id)
    Member.acceptApplicant(user, club)
    messages.add_message(request, messages.SUCCESS, "Application accepted!")
    return redirect('manage_applicants', club_id)


@login_required
@staff_required
def decline_application(request, club_id, user_id):
    """View that declines an applicant"""
    club = Club.objects.get(id = club_id)
    user = User.objects.get(id = user_id)
    Member.decline_application(user, club)
    messages.add_message(request, messages.WARNING, "Application declined!")
    return redirect('manage_applicants', club_id)

@login_required
@club_owner_required
def make_owner(request, club_id, user_id):
    """View that transfer ownership to other club member"""
    club = Club.objects.get(id = club_id)
    new_club_owner = User.objects.get(id = user_id)
    old_club_owner = request.user
    request_user_membership = Member.objects.get(club_membership=club, current_user=old_club_owner)
    if request_user_membership.user_type == UserTypes.CLUB_OWNER:
        request_user_membership.transferOwnership(new_club_owner, old_club_owner, club)
        messages.add_message(request, messages.SUCCESS, "Club ownership was reassigned!")
        return redirect('show_club', club_id)
    else:
        return redirect('feed')

@login_required
def apply_club(request, club_id):
    """View that creates a new applicant for the selected club"""
    user = request.user
    club = Club.objects.get(id=club_id)
    try:
        Member.objects.get(current_user=user, club_membership=club)
        messages.add_message(request, messages.ERROR, f"You're already a member of { club.name }!!")
    except ObjectDoesNotExist:
        Member.applyClub(user, club)
        messages.add_message(request, messages.SUCCESS, f"You just applied to { club.name }!!")
    finally:
        return redirect('feed')