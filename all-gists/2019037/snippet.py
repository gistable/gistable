# -*- coding: utf-8 -*-
"""
    wsgi_app

    A wsgi application script to load tryton and also the middleware required
    to support Cross Origin Resource Sharing (CORS).

    Inspired by the original work at http://codereview.tryton.org/92001/ by
    Cedric.

    :copyright: (c) 2011 by Cedric Krier
    :copyright: (c) 2012 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""

import sys
import json
import traceback
from BaseHTTPServer import BaseHTTPRequestHandler, DEFAULT_ERROR_MESSAGE

#: This parameter specifies the origin URLs from which the tryton server can
#: accept requests. While specifying '*' here might seem like a security hole
#: this is usually how your trytond runs anyway! listening to requests from 
#: all IPs
ALLOW_ORIGIN = "*"

#: These are the only headers that are required by the app 
ALLOW_HEADERS = "origin, x-requested-with, content-type"

#: If you have your config file in an unconventional location
CONFIG_PATH = 'trytond.conf'

from trytond.config import CONFIG
CONFIG.update_etc(CONFIG_PATH)
from trytond.protocols.jsonrpc import object_hook, JSONEncoder
from trytond.protocols.dispatcher import dispatch
from trytond.pool import Pool
from trytond.exceptions import UserError, UserWarning, NotLogged, \
    ConcurrencyException
Pool.start()


def jsonrpc_app(environ, start_response):
    'JSON-RPC dispatcher'
    if environ['REQUEST_METHOD'] == 'POST':
        body = ''
        try:
            length = int(environ.get('CONTENT_LENGTH', '0'))
        except ValueError:
            length = 0
        body = environ['wsgi.input'].read(length)
        rawreq = json.loads(body, object_hook=object_hook)
        req_id = rawreq.get('id', 0)
        method = rawreq['method']
        params = rawreq.get('params', [])

        response = {'id': req_id}
        database_name = environ['PATH_INFO'][1:]
        # TODO sao
        method_list = method.split('.')
        object_type = method_list[0]
        object_name = '.'.join(method_list[1:-1])
        method = method_list[-1]
        args = (environ['SERVER_NAME'], int(environ['SERVER_PORT']),
            'JSON-RPC', database_name, params[0], params[1], object_type,
            object_name, method) + tuple(params[2:])
        try:
            response['result'] = dispatch(*args)
        except (UserError, UserWarning, NotLogged,
                ConcurrencyException), exception:
            response['error'] = exception.args
        except Exception:
            tb_s = ''.join(traceback.format_exception(*sys.exc_info()))
            for path in sys.path:
                tb_s = tb_s.replace(path, '')
            # report exception back to server
            response['error'] = (str(sys.exc_value), tb_s)

        start_response('200 OK', [('Content-Type', 'application/json-rpc')])
        return [json.dumps(response, cls=JSONEncoder)]
    # TODO implement GET
    else:
        code = '501'
        message, explain = BaseHTTPRequestHandler.responses[code]
        start_response(code, [('Content-Type', 'text/html'),
                            ('Connection', 'close')])
        return [DEFAULT_ERROR_MESSAGE % locals()]


class TrytonWebMiddleware(object):
    """
    A Middleware class to extend the app to respond to OPTIONS request and
    support Cross-origin resource sharing.
    """
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'OPTIONS':
            # Most browser implementation of CORS sends an OPTIONS request 
            # first to test if the resource support XDomain requests.
            # So handle them 
            start_response('200 OK', [
                ('Access-Control-Allow-Origin', ALLOW_ORIGIN),
                ('Access-Control-Allow-Headers', ALLOW_HEADERS),
            ])
            return ['POST']
        else:
            def cors_start_response(status, headers, exc_info=None):
                headers.append(
                    ('Access-Control-Allow-Origin', ALLOW_ORIGIN)
                )
                headers.append(
                    ('Access-Control-Allow-Headers', ALLOW_HEADERS)
                )
                return start_response(status, headers, exc_info)

            return self.app(environ, cors_start_response)


application = TrytonWebMiddleware(jsonrpc_app)


if __name__ == '__main__':
    # This is not a really stable/healthy way to run the wsgi app
    # 
    # Install gunicorn using `pip install gunicorn` and then run the app
    # using the following command
    #
    # `gunicorn wsgi_app -b 0.0.0.0:8000`
    #
    # where wsgi_app is the name of this file
    #
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, application)
    httpd.handle_request()
