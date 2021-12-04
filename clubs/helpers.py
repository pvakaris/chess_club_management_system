from django.conf import settings
from django.shortcuts import redirect

def login_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN, SelectedClubTracker.instance().current_club)
        else:
            return view_function(request)
    return modified_view_function

class SelectedClubTracker(object):
    _instance = None
    current_club = 0

    def __init__(self):
        pass

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance
