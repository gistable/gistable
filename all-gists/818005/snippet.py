""" Monkey patch to hit wsgi apps when using urlfetch

This will monkey patch App Engine's urlfetch.fetch with a fetch that hits a local
wsgi app registered with add_intercept. This module is inspired by and borrows 
code from the wsgi-intercept project, which doesn't work with App Engine.

This is intended only for the local SDK environment for unit tests.

Usage:

from google.appengine.api import urlfetch
import urlfetch_intercept
urlfetch_intercept.install()
urlfetch_intercept.add_intercept('example.com', my_wsgi_app)

resp = urlfetch.fetch("http://example.com/foo")
...

"""
import urllib
import urlparse

from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import fetch as original_fetch
import webob

__all__ = ['install', 'uninstall', 'add_intercept', 'remove_intercept']

def install():
    urlfetch.fetch = wsgi_fetch

def uninstall():
    urlfetch.fetch = original_fetch
    
_intercepts = {}
def add_intercept(host, app):
    _intercepts[host] = app

def remove_intercept(host):
    del _intercepts[host]

def wsgi_fetch(url, payload=None, method=urlfetch.GET, headers={},
          allow_truncated=False, follow_redirects=True,
          deadline=None):

    url = urlparse.urlparse(url)
    app = _intercepts[url.netloc]
    
    req = webob.Request.blank(url.path)
    req.method = method
    for header in headers:
        req.headers[header] = headers[header]
    if payload:
        if isinstance(payload, str):
            req.body = payload
        else:
            req.body = urllib.urlencode(payload)

    resp = {}
    resp['content_was_truncated'] = False
    resp['final_url'] = url
    
    write_results = []
    def start_response(status, headers, exc_info=None):
        resp['status_code'] = status
        resp['headers'] = headers

        def write_fn(s):
            write_results.append(s)
        return write_fn
    
    # run the application.
    app_result = app(req.environ, start_response)
    result = iter(app_result)
    
    ###
    
    # read all of the results.  the trick here is to get the *first*
    # bit of data from the app via the generator, *then* grab & return
    # the data passed back from the 'write' function, and then return
    # the generator data.  this is because the 'write' fn doesn't
    # necessarily get called until the first result is requested from
    # the app function.
    #
    # see twill tests, 'test_wrapper_intercept' for a test that breaks
    # if this is done incorrectly.
    output = []
    try:
        generator_data = None
        try:
            generator_data = result.next()
    
        finally:
            for data in write_results:
                output.append(data)
    
        if generator_data:
            output.append(generator_data)
    
            while 1:
                data = result.next()
                output.append(data)
                
    except StopIteration:
        pass
    
    resp['content'] = ''.join(output)
    
    if hasattr(app_result, 'close'):
        app_result.close()
    
    class dictob(object):
        def __init__(self, d):
            self.__dict__ = d
    return dictob(resp)
