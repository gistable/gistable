# Read more at http://www.pindi.us/blog/migrating-cross-domain-cookies-django

from django.conf import settings
from importlib import import_module

class UpdateSessionCookieMiddleware(object):
    """
        Migrates session data from an old (hardcoded) session cookie name and domain to the name and
        domain currently defined in the Django settings.
        
        Should be placed after SessionMiddleware but before any middleware that uses request.session.
    """

    def process_request(self, request):
        session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
        if session_key is None:
            old_session_key = request.COOKIES.get('sessionid', None)
            if old_session_key:
                engine = import_module(settings.SESSION_ENGINE)
                old_session = engine.SessionStore(old_session_key)
                for key, value in old_session.items():
                    request.session[key] = value
            request.session.save()

    def process_response(self, response):
        response.delete_cookie('sessionid', domain='www.getstudyroom.com')