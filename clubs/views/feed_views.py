"""Feed related views."""
from django.conf import settings
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from clubs.models import Member, Club,Post

class FeedView(LoginRequiredMixin, ListView):
    """Class-based generic view for displaying a view."""

    model = Post
    template_name = "feed.html"
    context_object_name = 'posts'
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        """Return the user's feed."""
        user = self.request.user
        clubs = Club.objects.filter(
        id__in=Member.objects.filter(
            current_user=user).exclude(user_type = 4).values("club_membership")
        ).values("id")
        posts = Post.objects.filter(club_own_id__in=clubs).order_by('id')
        return posts

    def get_context_data(self, **kwargs):
        """Return context data, including myclubs and user."""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        context['myclubs'] = Member.objects.filter(current_user = user)
        return context