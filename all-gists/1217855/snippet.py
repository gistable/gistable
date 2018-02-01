import sys
from gevent import server
from gevent.baseserver import _tcp_listener
from gevent import pywsgi
from gevent.monkey import patch_all; patch_all()
from multiprocessing import Process, current_process, cpu_count

def hello_world(env, start_response):
    if env['PATH_INFO'] == '/':
        start_response('200 OK', [('Content-Type', 'text/html')])
        return ["<b>hello world</b>"]
    else:
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        return ['<h1>Not Found</h1>']

listener = _tcp_listener(('127.0.0.1', 8001))

def serve_forever(listener):
    pywsgi.WSGIServer(listener, hello_world).serve_forever()

number_of_processes = 5
print 'Starting %s processes' % number_of_processes
for i in range(number_of_processes):
    Process(target=serve_forever, args=(listener,)).start()

serve_forever(listener)