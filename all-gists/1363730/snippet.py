from StringIO import StringIO
from django.core.handlers.wsgi import WSGIRequest

def fake_get(path='/', user=None):
    req = WSGIRequest({
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': path,
            'wsgi.input': StringIO()})
    from django.contrib.auth.models import AnonymousUser
    req.user = AnonymousUser() if user is None else user
    return req
