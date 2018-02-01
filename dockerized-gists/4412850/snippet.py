#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import session, g, Flask, request, abort
app = Flask(__name__)

urls = (
    '/song/<int:sid>', 'Song',
)

class Song():
    def GET(self, sid):
        return 'Song %s' % str(sid)

def init_mapping(mapping):
    return list(group(mapping, 2))

""" webpy style router """
def group(seq, size):
    """
    Returns an iterator over a series of lists of length size from iterable.

        >>> list(group([1,2,3,4], 2))
        [[1, 2], [3, 4]]
        >>> list(group([1,2,3,4,5], 2))
        [[1, 2], [3, 4], [5]]
    """
    def take(seq, n):
        for i in xrange(n):
            yield seq.next()

    if not hasattr(seq, 'next'):
        seq = iter(seq)
    while True:
        x = list(take(seq, size))
        if x:
            yield x
        else:
            break

for route, what in init_mapping(urls):
    fvars = locals()
    what_class = fvars.get(what)

    def build_router_function(cls):
        def _inner(*args, **kwargs):
            view_class = cls()
            try:
                func = getattr(view_class, request.method.upper())
                return func(*args, **kwargs)
            except AttributeError:
                return abort(405)
        return _inner

    app.add_url_rule(route, what, build_router_function(what_class))
