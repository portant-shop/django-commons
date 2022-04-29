from django.conf import settings

from django.contrib.auth.decorators import user_passes_test


def anonymous_required(function=None):
    """Check and allow access only if user is anonymous."""
    decorator = user_passes_test(
        lambda u: not u.is_authenticated,
        login_url=settings.LOGIN_REDIRECT_URL,
        redirect_field_name=None
    )
    return decorator
