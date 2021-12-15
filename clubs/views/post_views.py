"""Post creation views."""
from django.contrib import messages
from django.shortcuts import redirect, render
from clubs.forms import PostForm
from clubs.models import Club,Post,Member
from clubs.helpers import club_owner_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.utils.decorators import method_decorator

class PostMessagesView(LoginRequiredMixin, CreateView):
    
    model = Post
    template_name = 'post_messages.html'
    form_class = PostForm
    http_method_names = ['post','get']
    
    @method_decorator(club_owner_required)
    def get(self,request,club_id):
    # get the post form. 
        current_user = request.user
        myClubs = Member.objects.filter(current_user = current_user)
        form = PostForm()
        return render(request, 'post_messages.html', {'form': form,'club_id':club_id,'myclubs':myClubs})
    
    @method_decorator(club_owner_required)
    def post(self,request,club_id):
        # post the post form. 
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


