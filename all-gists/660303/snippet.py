# -*- encoding: utf-8 -*-
# Usage:
# urlpatterns += patterns('',
#     route(r'^$', GET='getview', POST='postview', name='viewname'),
# )
#
from django.http import Http404
from django.core.urlresolvers import RegexURLPattern, get_callable

def discover_view(view, prefix=''):
    if isinstance(view, basestring):
        if not view:
            raise ValueError('View name is required to discover the callable')
        if prefix:
            view = prefix + '.' + view
        return get_callable(view)
    else:
        return view


class ViewByMethod(object):
    def __init__(self, GET=None, POST=None):
        self.GET = GET
        self.POST = POST

    def __call__(self, request, *args, **kwargs):
        if request.method == 'GET' and self.GET:
            return self.GET(request, *args, **kwargs)
        elif request.method == 'POST' and self.POST:
            return self.POST(request, *args, **kwargs)
        raise Http404


class RegexUrlPatternByMethod(RegexURLPattern):
    def __init__(self, regex, GET=None, POST=None, default_args=None, name=None):
        super(RegexUrlPatternByMethod, self).__init__(regex, '', default_args, name)
        self.GET = GET
        self.POST = POST

    def add_prefix(self, prefix):
        self.prefix = prefix

    def _get_callback(self):
        callable_get = discover_view(self.GET, self.prefix)
        callable_post = discover_view(self.POST, self.prefix)

        return ViewByMethod(callable_get, callable_post)
    callback = property(_get_callback)


def route(regex, GET=None, POST=None, kwargs=None, name=None, prefix=''):
    return RegexUrlPatternByMethod(regex, GET, POST, kwargs, name)
