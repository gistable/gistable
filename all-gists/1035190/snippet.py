# https://gist.github.com/1035190
# See also: Snippets 85, 240, 880 at http://www.djangosnippets.org/
#
# Minimally, the following settings are required:
#
#     SSL_ENABLED = True
#     SSL_URLS = (
#        r'^/some/pattern/',
#     )


import re
from django.http import HttpResponseRedirect, get_host
from django.conf import settings


SSL_ENABLED = getattr(settings, 'SSL_ENABLED', False)
SSL_URLS = getattr(settings, 'SSL_URLS', [])
SSL_IGNORE_URLS = getattr(settings, 'SSL_IGNORE_URLS', [])
HTTP_HOST = getattr(settings, 'HTTP_HOST', None)
HTTPS_HOST = getattr(settings, 'HTTPS_HOST', None)


class SSLRedirectMiddleware:
    """
    Django middleware that redirects to https if the requested path matches
    a pattern in SSL_URLS.
    """

    secure_urls = tuple([re.compile(url) for url in SSL_URLS])
    ignore_urls = tuple([re.compile(url) for url in SSL_IGNORE_URLS])

    def process_request(self, request):
        if not SSL_ENABLED:
            return
        secure = False
        ignore = False
        for url in self.ignore_urls:
            if url.match(request.path):
                ignore = True
                break
        if not ignore:
            for url in self.secure_urls:
                if url.match(request.path):
                    secure = True
                    break
            if not secure == self._is_secure(request):
                return self._redirect(request, secure)

    def _is_secure(self, request):
        if request.is_secure():
            return True
        return False

    def _redirect(self, request, secure):
        protocol = secure and 'https' or 'http'
        if secure:
            host = HTTPS_HOST or get_host(request)
        else:
            host = HTTP_HOST or get_host(request)
        url = '%s://%s%s' % (protocol, host, request.get_full_path())
        if settings.DEBUG and request.method == 'POST':
            raise RuntimeError, "Django can't perform an SSL redirect while " \
                + "maintaining POST data. Please structure your views so " \
                + "that redirects only occur during GETs."
        return HttpResponseRedirect(url)
