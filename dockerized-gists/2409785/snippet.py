#!/usr/bin/python
#based on the ideas from http://synack.me/blog/implementing-http-live-streaming
# Run this script and then launch the following pipeline:
# gst-launch videotestsrc pattern=ball ! video/x-raw-rgb, framerate=15/1, width=640, height=480 !  jpegenc ! multipartmux boundary=spionisto ! tcpclientsink port=9999

from Queue import Queue
from threading import Thread
from socket import socket
from select import select
from wsgiref.simple_server import WSGIServer, make_server, WSGIRequestHandler
from SocketServer import ThreadingMixIn


class MyWSGIServer(ThreadingMixIn, WSGIServer):
     pass 

def create_server(host, port, app, server_class=MyWSGIServer,  
          handler_class=WSGIRequestHandler):
     return make_server(host, port, app, server_class, handler_class) 

INDEX_PAGE = """
<html>
<head>
    <title>Gstreamer testing</title>
</head>
<body>
<h1>Testing a dummy camera with GStreamer</h1>
<img src="/mjpeg_stream"/>
<hr />
</body>
</html>
"""
ERROR_404 = """
<html>
  <head>
    <title>404 - Not Found</title>
  </head>
  <body>
    <h1>404 - Not Found</h1>
  </body>
</html>
"""


class IPCameraApp(object):
    queues = []

    def __call__(self, environ, start_response):    
        if environ['PATH_INFO'] == '/':
            start_response("200 OK", [
                ("Content-Type", "text/html"),
                ("Content-Length", str(len(INDEX_PAGE)))
            ])
            return iter([INDEX_PAGE])    
        elif environ['PATH_INFO'] == '/mjpeg_stream':
            return self.stream(start_response)
        else:
            start_response("404 Not Found", [
                ("Content-Type", "text/html"),
                ("Content-Length", str(len(ERROR_404)))
            ])
            return iter([ERROR_404])

    def stream(self, start_response):
        start_response('200 OK', [('Content-type', 'multipart/x-mixed-replace; boundary=--spionisto')])
        q = Queue()
        self.queues.append(q)
        while True:
            try:
                yield q.get()
            except:
                if q in self.queues:
                    self.queues.remove(q)
                return


def input_loop(app):
    sock = socket()
    sock.bind(('', 9999))
    sock.listen(1)
    while True:
        print 'Waiting for input stream'
        sd, addr = sock.accept()
        print 'Accepted input stream from', addr
        data = True
        while data:
            readable = select([sd], [], [], 0.1)[0]
            for s in readable:
                data = s.recv(1024)
                if not data:
                    break
                for q in app.queues:
                    q.put(data)
        print 'Lost input stream from', addr

if __name__ == '__main__':

    #Launch an instance of wsgi server
    app = IPCameraApp()
    port = 1337
    print 'Launching camera server on port', port
    httpd = create_server('', port, app)

    print 'Launch input stream thread'
    t1 = Thread(target=input_loop, args=[app])
    t1.setDaemon(True)
    t1.start()

    try:
        print 'Httpd serve forever'
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.kill()
        print "Shutdown camera server ..."
