#!/usr/bin/python

import SimpleHTTPServer
import SocketServer
import logging
import cgi

PORT = 8001
I = '0.0.0.0'

def procmsg(data):
	#Do something with your SMS here
	print "Message recieved from: " + data['iccid'] + " sent to: " + data['destination'] + " containing the text: " + data['message']
	
	


class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200, 'OK')
		self.send_header('Content-type', 'text/html')
		self.send_header('Content-length', '0')
		self.end_headers()
	def do_POST(self):
		form = cgi.FieldStorage(
			fp=self.rfile,
			headers=self.headers,
			environ={'REQUEST_METHOD':'POST',
				'CONTENT_TYPE':self.headers['Content-Type'],
				})
		data = {}
		for f in form.list:
			data[f.name] = f.value
		procmsg(data)
		SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)


Handler = ServerHandler
httpd = SocketServer.TCPServer((I, PORT), Handler)

print "Serving at: http://%(interface)s:%(port)s" % dict(interface=I or "localhost", port=PORT)
httpd.serve_forever()