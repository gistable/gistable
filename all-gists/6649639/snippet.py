# -*- coding: utf-8 -*-
"""
    Inspiration taken from Flask-Exceptiopn 
    :copyright: (c) 2012 by Jonathan Zempel.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import with_statement

from flask import _request_ctx_stack as stack, redirect
from functools import wraps

from .models import Redirect


class QuokkaRedirect(object):

    def init_app(self, app):
        """Initialize this Exceptional extension.

        :param app: The Flask application to track errors for.
        """
        if not hasattr(app, "extensions"):
            app.extensions = {}

        if "quokka-redirect" in app.extensions:
            app.logger.warning("Repeated Quokka-redirect initialization attempt.")
        else:
            app.handle_http_exception = self._get_http_exception_handler(app)
            app.extensions["quokka-redirect"] = self

    def _get_http_exception_handler(self, app):
        """Get a wrapped HTTP exception handler. Returns a handler that can
        be used to override Flask's ``app.handle_http_exception``. The wrapped
        handler redirects if it exists in Redirect document

        :param app: The app for which the HTTP exception handler is being
            wrapped.
        """
        handle_http_exception = app.handle_http_exception

        @wraps(handle_http_exception)
        def ret_val(exception):
            context = stack.top
            request = context.request
            #  Full url, e.g.,
            #  http://example.com/channel/page.html?x=y
            url = request.url
            #  Previous url maps to
            #  http://example.com/channel/
            url_root = request.url_root
            #  Removes the query parameters
            base_url = request.base_url
            #  /channel
            script_root = request.script_root
            #  /page.html
            path = request.path
            if path.startswith('/'):
                path = path[1:]
            paths = path.split('/')
            mpath = ",".join(paths)
            mpath = ",{0},".format(mpath)
            if exception.code in [404,]:
                try: 
                    redirect_to = Redirect.objects.get(linkname=path)
                    target = redirect_to.target
                    long_slug = target.get_absolute_url()
                except:            
                    return handle_http_exception(exception)
                return redirect(long_slug)
        return ret_val
