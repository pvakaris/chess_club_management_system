"""system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from clubs import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('log_in/', views.log_in, name='log_in'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('edit_club/', views.edit_club, name='edit_club'),
    path('user/<int:user_id>', views.show_user, name='show_user'),
    path('club/<int:club_id>', views.show_club, name='show_club'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('log_out/', views.log_out, name='log_out'),
    path('feed/', views.feed, name='feed'),
    path('members/', views.MemberListView.as_view(), name='member_list'),
    path('clubs/', views.ClubListView.as_view(), name='club_list'),
    path('apply/', views.apply, name='apply'),
    path('create_club/', views.create_club, name='create_club'),
    path('members/<int:club_id>', views.club_members , name='club_members'),
    path('manage_officers/', views.manage_officers , name='manage_officers'),
    path('manage_applicants/', views.manage_applicants , name='manage_applicants'),
    path('promote_member/', views.promote_member , name='promote_member'),
    path('demote_officer/', views.demote_officer , name='demote_officer'),
    path('accept_application/', views.accept_application , name='accept_application'),
    path('decline_application/', views.decline_application , name='decline_application')
    #path('members/<int:club_id>', views.ClubMemberListView.as_view() , name='club_members')
]
