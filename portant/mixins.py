from django.conf import settings
from django.http import HttpResponseRedirect


class AnonymousRequiredMixin:
    """Verify that the current user is anonymous."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        return super().dispatch(request, *args, **kwargs)
