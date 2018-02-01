#!/usr/bin/env python

# Author: Samat Jain <http://samat.org/>
# License: MIT (same as Bottle)

import bottle

from bottle import request, response, route
from bottle import install, uninstall

from json import dumps as json_dumps


class JSONAPIPlugin(object):
    name = 'jsonapi'
    api = 1

    def __init__(self, json_dumps=json_dumps):
        uninstall('json')
        self.json_dumps = json_dumps

    def apply(self, callback, context):
        dumps = self.json_dumps
        if not dumps: return callback
        def wrapper(*a, **ka):
            r = callback(*a, **ka)

            # Attempt to serialize, raises exception on failure
            json_response = dumps(r)

            # Set content type only if serialization succesful
            response.content_type = 'application/json'

            # Wrap in callback function for JSONP
            callback_function = request.query.get('callback')
            if callback_function:
                json_response = ''.join([callback_function, '(', json_response, ')'])

            return json_response
        return wrapper


install(JSONAPIPlugin())


@route('/')
def hello():
    r = [{'hello': 'world'}]
    r.append({1: 2})
    return r

if __name__ == '__main__':
    from bottle import run
    run(reloader=True)