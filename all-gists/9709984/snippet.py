from functools import wraps

from django.conf import settings
from django.http import HttpResponseRedirect


def require_ssl(view):
    """
    Decorator that requires an SSL connection.  If the current connection is not SSL, we redirect to the SSL version of
    the page.
    """
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not settings.DEBUG and not request.is_secure():
            # Redirect!
            target_url = "https://" + request.META['HTTP_HOST'] + request.path_info
            return HttpResponseRedirect(target_url)
        return view(request, *args, **kwargs)
    return wrapper