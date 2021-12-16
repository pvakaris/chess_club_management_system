"""View mixins."""
from django.shortcuts import redirect
from django.core.exceptions import ImproperlyConfigured

class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        """Returns the url to redirect to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        else:
            return self.redirect_when_logged_in_url

class ClubOwnerRequiredMixin:
    """Mixin that redirects when a user is not the club owner"""

    redirect_when_not_club_owner_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when not a club owner, or dispatch as normal otherwise."""
        if self.request.user.user_type != UserTypes.OWNER:
            return self.handle_not_club_owner(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_not_club_owner(self, *args, **kwargs):
        url = self.get_redirect_when_not_club_owner_url()
        return redirect(url)

    def get_redirect_when_not_club_owner_url(self):
        """Returns the url to redirect to when not logged in."""
        if self.redirect_when_not_club_owner_url is None:
            raise ImproperlyConfigured(
                "ClubOwnerRequiredMixin requires either a value for "
                "'redirect_when_not_club_owner_url', or an implementation for "
                "'get_redirect_when_not_club_owner_url()'."
            )
        else:
            return self.redirect_when_not_club_owner_url
