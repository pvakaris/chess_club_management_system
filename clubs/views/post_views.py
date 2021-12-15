"""Post creation views."""
from django.contrib import messages
from django.shortcuts import redirect, render
from clubs.forms import PostForm
from django.contrib.auth.decorators import login_required
from clubs.models import Club,Post,Member
from django.urls import reverse
from clubs.helpers import club_owner_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.http import Http404

@login_required
@club_owner_required
def post_messages(request,club_id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            current_user = request.user
            myClubs = Member.objects.filter(current_user = current_user)
            club = Club.objects.get(id = club_id)
            form = PostForm(request.POST)
            if form.is_valid():
                message = form.cleaned_data.get('message')
                post = Post.objects.create(author=current_user, message=message,club_own=club)
                messages.add_message(request, messages.SUCCESS, "Post was created!")
                return redirect('feed')
            else:
                return render(request, 'post_messages.html', {'form': form,'club_id':club_id,'myclubs':myClubs})
        else:
            form = PostForm()
            return render(request, 'post_messages.html', {'form': form,'club_id':club_id})
    else:
        if request.user.is_authenticated:
            current_user = request.user
            myClubs = Member.objects.filter(current_user = current_user)
            form = PostForm()
            return render(request, 'post_messages.html', {'form': form,'club_id':club_id,'myclubs':myClubs})
