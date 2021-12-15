"""Feed related views."""
from django.shortcuts import render
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from clubs.models import Member, Club,Post
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage,InvalidPage

@login_required #TODO show the amount of club members
def feed(request):
    """View for displaying a feed."""
    user = request.user
    clubs = Club.objects.filter(
    id__in=Member.objects.filter(
        current_user=user).exclude(user_type = 4).values("club_membership")
    ).values("id")
    posts = Post.objects.filter(club_own_id__in=clubs).order_by('id')
    members = Member.objects.filter(current_user = user)
    paginator = Paginator(posts, 10)
    try:
        page_number = request.GET.get('page', '1')
        page = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage, InvalidPage):
        page = paginator.page(1)

    return render(request, 'feed.html', {'user': user, 'myclubs': members,'page':page})