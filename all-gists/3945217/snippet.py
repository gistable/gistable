# encoding: utf-8

"""
A simple development webserver for the console that features
throttling (if enabled by -t) and ignores query strings.
"""

import SimpleHTTPServer
import SocketServer
import os
import time
from optparse import OptionParser

PORT = 8000


class CustomHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def __init__(self, req, client_addr, server):
        #print req, client_addr, server
        SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, req, client_addr, server)

    def do_GET(self):
        # cut off a query string
        if '?' in self.path:
            self.path = self.path.split('?')[0]
        if options.throttle:
            delay = 0.5  # standard roundtrip time delay
            if os.path.exists(self.path[1:]):
                # delay for files, proportional with size
                size = os.path.getsize(self.path[1:])
                delay += (float(size) / float(1024 * 1024)) * 5.0  # 5 seconds per MB
            time.sleep(delay)
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)


class MyTCPServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-t", "--throttle", dest="throttle",
        help="Activate throttling", action="store_true")
    (options, args) = parser.parse_args()
    httpd = MyTCPServer(('localhost', PORT), CustomHandler)
    httpd.allow_reuse_address = True
    print "Serving at port", PORT
    if options.throttle:
        print "Throttling activated"
    httpd.serve_forever()
