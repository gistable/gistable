#!/usr/bin/env python
""" Test HTTP Server 

This script starts a http server that will respond to HTTP requests
with a predefined response.

Usage:

  ./http_server.py --port=8080 --code=404 --content="Page not Found"

  ./http_server.py --port=8080 --code=500 --content="Internal Server Error"

"""

import sys, os

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from optparse import OptionParser

class APIHandler(BaseHTTPRequestHandler, object):

  def __init__(self, *args, **kwargs):
    super(APIHandler, self).__init__(*args, **kwargs)

  def do_request(self):
    global options
    
    self.send_response(int(options.code))
    
    self.send_header('Content-type', options.type)
    self.end_headers()
    
    self.wfile.write(options.content)
    
  def do_GET(self):
    return self.do_request()
    
  def do_POST(self):
    return self.do_request()

def main():
  global options
  options, args = parse_cli()
  
  server_address = ('', int(options.port))
  httpd = HTTPServer(server_address, APIHandler)

  try:
    httpd.serve_forever()
    
  except KeyboardInterrupt:
    httpd.socket.close()

def parse_cli():
  parser = OptionParser()
  
  parser.add_option('-p', '--port', default=8000)
  
  parser.add_option('', '--code', default=200, \
    help="request return code")
    
  parser.add_option('', '--type', default='text/html', \
    help="content type")
    
  parser.add_option('', '--content', default='')
  
  return parser.parse_args()

if __name__ == '__main__':
  sys.exit(main())
