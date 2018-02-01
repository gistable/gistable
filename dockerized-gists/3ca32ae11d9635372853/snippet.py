#!/usr/bin/env python

import SimpleHTTPServer
import BaseHTTPServer
import sys

"""
Usage:
    python httpd.py [port] [additional headers ...]

Example:
    python httpd.py 8000 'Pragma: no-cache' 'Cache-Control: no-cache' 'Expires: 0'
"""

class CustomHTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_new_headers()

        SimpleHTTPServer.SimpleHTTPRequestHandler.end_headers(self)

    def send_new_headers(self):
        for i in sys.argv[2:]:
            key, value = i.split(":", 1)
            self.send_header(key, value)

if __name__ == '__main__':
    BaseHTTPServer.test(HandlerClass=CustomHTTPRequestHandler, ServerClass = BaseHTTPServer.HTTPServer, protocol="HTTP/1.1")
