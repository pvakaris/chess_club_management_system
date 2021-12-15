"""Post creation views."""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import redirect, render
from clubs.forms import PostForm
from django.contrib.auth.decorators import login_required
from clubs.models import Club,Post
from clubs.helpers import club_owner_required


@login_required
@club_owner_required
def post_messages(request,club_id):
    """View for new post handling."""
    if request.method == 'POST':
        if request.user.is_authenticated:
            current_user = request.user
            club = Club.objects.get(id = club_id)
            form = PostForm(request.POST)
            if form.is_valid():
                message = form.cleaned_data.get('message')
                post = Post.objects.create(author=current_user, message=message,club_own=club)
                messages.add_message(request, messages.SUCCESS, "Post was created!")
                return redirect('feed')
            else:
                return render(request, 'post_messages.html', {'form': form,'club_id':club_id})
        else:
            form = PostForm()
            return render(request, 'post_messages.html', {'form': form,'club_id':club_id})
    else:
        if request.user.is_authenticated:
            form = PostForm()
            return render(request, 'post_messages.html', {'form': form,'club_id':club_id})