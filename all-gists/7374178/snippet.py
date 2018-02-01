# --- [middleware helper to serve static resources] ---
# Placed in public domain

import os
import mimetypes

# directory with static resources (default: 'static' in current dir)
STATIC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))

def appstatic(app, environ, start_response):
    """WSGI app/middleware to serve files from /static endpoint"""
    if environ['SCRIPT_NAME'] != '/static':
        return app(environ, start_response)
    else:
        path = os.path.abspath(
                 os.path.join(STATIC_PATH, environ['PATH_INFO'].lstrip('/')))
        if not path.startswith(STATIC_PATH) or\
           not os.path.exists(path):
            start_response("404 not found", [('Content-type', 'text/plain')])
            return ['File Not Found: %s\n' % environ['PATH_INFO'],
                    'STATIC_PATH: %s\n' % STATIC_PATH,
                    'Joined path: %s' % path]
        else:
            filetype = mimetypes.guess_type(path, strict=True)[0]
            if not filetype:
                filetype = 'text/plain'
            start_response("200 OK", [('Content-type', filetype)])
            return environ['wsgi.file_wrapper'](open(path, 'rb'), 4096)


# wrapper example
#  from functools import partial
#  wrapped = partial(appstatic, partial(static, application))

#  from wsgiref.simple_server import make_server
#  httpd = make_server('', 8080, wrapped)
#  print("Serving on port 8080..")
#  httpd.serve_forever()
