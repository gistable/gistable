"""
Simple forking echo server built with Python's SocketServer library. A more
Pythonic version of http://gist.github.com/203520, which itself was inspired
by http://tomayko.com/writings/unicorn-is-unix.
"""

import os
import SocketServer

class EchoHandler(SocketServer.StreamRequestHandler):
    def handle(self):
         self.wfile.write('Child %s echo>' % os.getpid())
         self.wfile.flush()
         message = self.rfile.readline()
         self.wfile.write(message)
         print "Child %s echo'd: %r" % (os.getpid(), message)
             
if __name__ == '__main__':
    server = SocketServer.ForkingTCPServer(('localhost', 4242), EchoHandler)
    print "Server listening on localhost:4242..."
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print "\nbailing..."