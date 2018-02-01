from types import MethodType

from django.http import CompatCookie, HttpRequest


def _set_cookie(self, key, value='', max_age=None, expires=None, path='/',
           domain=None, secure=False):
    self._resp_cookies[key] = value
    self.COOKIES[key] = value
    if max_age is not None:
        self._resp_cookies[key]['max-age'] = max_age
    if expires is not None:
        self._resp_cookies[key]['expires'] = expires
    if path is not None:
        self._resp_cookies[key]['path'] = path
    if domain is not None:
        self._resp_cookies[key]['domain'] = domain
    if secure:
        self._resp_cookies[key]['secure'] = True


def _delete_cookie(self, key, path='/', domain=None):
    self.set_cookie(key, max_age=0, path=path, domain=domain,
                    expires='Thu, 01-Jan-1970 00:00:00 GMT')
    try:
        del self.COOKIES[key]
    except KeyError:
        pass


class RequestCookies(object):
    """
    Allows setting and deleting of cookies from requests in exactly the same
    way as responses.
    
    >>> request.set_cookie('name', 'value')
    
    The set_cookie and delete_cookie are exactly the same as the ones built
    into the Django HttpResponse class. 

    http://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse.set_cookie
    """
    def process_request(self, request):

        request._resp_cookies = CompatCookie()
        request.set_cookie = MethodType(_set_cookie, request, HttpRequest)
        request.delete_cookie = MethodType(_delete_cookie, request, HttpRequest)
    
    def process_response(self, request, response):
        if hasattr(request, '_resp_cookies') and request._resp_cookies:
            response.cookies.update(request._resp_cookies)
        
        return response
