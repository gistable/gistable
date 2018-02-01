# coding: utf-8

# Profiling middleware and decorator, that allows to profile any django
# view easily for superusers.

__author__ = 'igor.katson@gmail.com'

import cProfile
import pstats
import tempfile

import cStringIO as StringIO


def profile_view(func):
    """A view decorator that allows profiling.

    Usage:
    /path/to/view/?profile=1
    /path/to/view/?profile=1&print_callees=1
    /path/to/view/?profile=1&print_callers=1
    /path/to/view/?profile=1&profile_limit=100
    /path/to/view/?profile=1&profile_order=time
    
    This will print the pstats.Stats profiling report right to
    your screen, as a content of Django response.
    """

    def inner(request, *args, **kwargs):
        if 'profile' not in request.GET:
            return func(request, *args, **kwargs)
        profile_order = request.GET.get('profile_order', 'cumulative')
        print_callees = request.GET.get('print_callees')
        print_callers = request.GET.get('print_callers')
        profile_limit = int(request.GET.get('profile_limit', 80))
        pfile = tempfile.NamedTemporaryFile()
        result = {}

        def wrapper():
            result_ = func(request, *args, **kwargs)
            result['result'] = result_
            return result_

        cProfile.runctx('wrapper()', globals(), locals(), pfile.name)
        stream = StringIO.StringIO()
        stats = pstats.Stats(pfile.name, stream=stream)
        stats = stats.sort_stats(profile_order)

        if print_callees:
            stats.print_callees(profile_limit)
        elif print_callers:
            stats.print_callers(profile_limit)
        else:
            stats.print_stats(profile_limit)

        response = result['result']
        text = stream.getvalue()
        
        # text/plain results use {line-break: break-word} by default in Chrome,
        # which makes long output of e.g. "print_callees=1" hard to read.
        # See http://stackoverflow.com/questions/5837556/how-to-disable-word-
        # wrapping-in-plain-text-files-in-chrome and
        # http://habrahabr.ru/company/mailru/blog/201778/#comment_6971294
        
        html = '<pre>%s</pre>' % text
        response.content = html
        response['Content-Type'] = 'text/html'
        return response
    return inner


class ProfilingMiddleware(object):
    """Profiling middleware, that allows to profile any django view easily.

    For usage examples, see profile_view decorator.
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        if 'profile' in request.GET and request.user.is_superuser:
            return profile_view(view_func)(request, *view_args, **view_kwargs)