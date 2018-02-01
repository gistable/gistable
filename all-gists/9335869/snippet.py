from re import compile

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login

if hasattr(settings, "LOGIN_REQUIRED_URLS"):
    URLS = [compile(expr) for expr in settings.LOGIN_REQUIRED_URLS]


class ActiveUserRequiredMiddleware:
    """
    Middleware that requires a user to be active to view any page specified in
    settings.LOGIN_REQUIRED_URLS. Since these urls are reguralar expressions,
    you can copy them from your urls.py.

    Requires authentication middleware and template context processors to be
    loaded. You'll get an error if they aren't.
    """
    def process_request(self, request):
        path = request.path_info.lstrip("/")
        if any(u.match(path) for u in URLS):
            if not request.user.is_active:
                next_url = request.get_full_path()
                return redirect_to_login(next_url, settings.LOGIN_URL,
                                         REDIRECT_FIELD_NAME)
