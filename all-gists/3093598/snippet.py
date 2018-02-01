from wsgiref.simple_server import make_server, WSGIServer
from SocketServer import ThreadingMixIn
from time import sleep


def simple_app(env, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/plain')]
    start_response(status, headers)

    sleep(10)
    return 'Hello World\n'


class ThreadingWSGIServer(ThreadingMixIn, WSGIServer): 
    pass


httpd = make_server('', 8000, simple_app, ThreadingWSGIServer)
print 'Listening on port 8000....'
httpd.serve_forever()