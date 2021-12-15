"""Member related views"""
from django.conf import settings
from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from clubs.models import User, Member, Club
from clubs.helpers import club_owner_required, member_required, staff_required
from clubs.user_types import UserTypes
from django.db.models import Q


@login_required
@member_required
def club_member(request, club_id, user_id):
    """View that shows a club member"""
    user = User.objects.get(id=user_id)
    club = Club.objects.get(id=club_id)
    current_user = request.user
    myClubs = Member.objects.filter(current_user = current_user)
    member = Member.objects.get(current_user=current_user, club_membership=club)
    if(member.user_type == UserTypes.MEMBER):
        return render(request, 'show_user.html', {'user': user, 'myclubs':myClubs})
    else:
        return render(request, 'show_user_full.html', {'user': user, 'myclubs':myClubs})

@login_required
@member_required
def club_members(request, club_id):
    """View that shows all club members"""
    user = request.user
    club = Club.objects.get(id = club_id)
    members = Member.objects.filter(
        Q(user_type = UserTypes.MEMBER, club_membership=club) |
        Q(user_type = UserTypes.OFFICER, club_membership=club) |
        Q(user_type = UserTypes.CLUB_OWNER, club_membership=club)
    )
    myClubs = Member.objects.filter(current_user = user)
    user_membership = Member.objects.get(current_user = user, club_membership = club)
    user_type = user_membership.user_type

    if user_type == UserTypes.CLUB_OWNER:
        return render(request, 'club_member_list.html', {'members' : members, 'club': club, 'is_owner': True, 'request_user_id': user.id, 'myclubs':myClubs})
    else:
        return render(request, 'club_member_list.html', {'members' : members, 'club': club, 'is_owner': False, 'request_user_id': user.id, 'myclubs': myClubs})

@login_required
@staff_required
def manage_applicants(request, club_id):
    """View that shows all applicants of a club"""
    user = request.user
    myClubs = Member.objects.filter(current_user = user)
    club = Club.objects.get(id = club_id)
    applicants = Member.objects.filter(club_membership=club, user_type=UserTypes.APPLICANT)
    return render(request, 'manage_applicants.html', {'applicants': applicants, 'club': club, 'applicants_count': applicants.count(), 'myclubs':myClubs})

@login_required
@club_owner_required
def manage_officers(request, club_id):
    """View that shows all officers of a club"""
    user = request.user
    myClubs = Member.objects.filter(current_user = user)
    club = Club.objects.get(id = club_id)
    officers = Member.objects.filter(club_membership=club, user_type=UserTypes.OFFICER)
    return render(request, 'manage_officers.html', {'officers' : officers, 'club' : club, 'officers_count': officers.count(), 'myclubs':myClubs})


class MemberListView(LoginRequiredMixin, ListView):
    """ View that shows a list of all members. """

    model = Member
    template_name = "member_list.html"
    context_object_name = "members"
    paginate_by = settings.MEMBERS_PER_PAGE

    def get_queryset(self):
        # We filter out all the users that are not APPLICANTS (user_type 4) and the members are sorted by first name
        memberships = Member.objects.filter(
            Q(user_type = UserTypes.CLUB_OWNER) |
            Q(user_type = UserTypes.OFFICER) |
            Q(user_type = UserTypes.MEMBER)
        )
        memberset = set()
        for member in memberships:
            for user in User.objects.all():
                if user.username == member.current_user.username:
                    memberset.add(user.username)
        members = User.objects.filter(username__in = memberset).order_by('first_name')
        return members

    def get_context_data(self, **kwargs):
        """Return context data"""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['myclubs'] = Member.objects.filter(current_user = user)
        return context
