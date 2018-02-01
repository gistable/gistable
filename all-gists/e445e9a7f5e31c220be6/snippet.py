#!/usr/bin/env python

# execute in the folder you want the server to run
# starts at port 80

import os
import urlparse
import SimpleHTTPServer
import SocketServer

HOST = ('0.0.0.0', 80)

class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	def do_GET(self):
		urlparts = urlparse.urlparse(self.path)
		request_file_path = urlparts.path.strip("/")

		print request_file_path

		if not os.path.exists(request_file_path):
			self.path = 'index.html'

		return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

httpd = SocketServer.TCPServer(HOST, Handler)
httpd.serve_forever()
