'''
Created on Nov 23, 2012

@author: uolter
'''


from functools import wraps
from flask import request, current_app


def jsonp(func):
    """Wraps JSONified output for JSONP requests."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            response = func(*args, **kwargs)
            data = str(response.data)
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            response = current_app.response_class(content, mimetype=mimetype, status=response.status_code)
            return response
        else:
            return func(*args, **kwargs)
    return decorated_function