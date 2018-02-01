#!/usr/bin/env python3
# -*- mode: python; coding: utf-8 -*-

assert str is not bytes

import my_example_1_wsgi as _my_example_1_wsgi
import my_example_2_wsgi as _my_example_2_wsgi
import my_example_3_wsgi as _my_example_3_wsgi

_application_by_host_dict = {
    'www.my-example-1.com': _my_example_1_wsgi.application,
    'www.my-example-2.org': _my_example_2_wsgi.application,
    'www.my-example-3.net': _my_example_3_wsgi.application,
}

def application(environ, start_response):
    host = environ.get('HTTP_HOST')
    
    selected_application = _application_by_host_dict.get(host)
    
    if selected_application is None:
        response_body = 'no application for this host'
        
        start_response('404 Not Found', [
            ('Content-Type', 'text/plain;charset=utf-8'),
        ])
        yield response_body.encode()
        
        return
    
    yield from selected_application(environ, start_response)

#
# Below for testing only
#
if __name__ == '__main__':
    from wsgiref import simple_server as _simple_server
    _httpd = _simple_server.make_server('localhost', 8051, application)
    _httpd.serve_forever()
