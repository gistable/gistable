#
# Run this under your WSGI server, and then try
#
#     curl -N -i <server>
#
# If you're chunked, you should see the pause between "hello" and "world".

import time

def application(environ, start_response):
    """Simplest possible application object"""
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    
    def resp():
        yield "hello "
        time.sleep(1)
        yield "world!\n"
        
    return resp()
