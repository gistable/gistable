# -*- coding= utf-8 -*-
import datetime
import os
import json
import tornado.ioloop
import tornado.web
import tornado
import tornado.httpclient
import traceback
import urllib2
import base64
import functools
import hashlib,base64,random

API_KEYS = {
	'rjtzWc674hDxTSWulgETRqHrVVQoI3T8f9RoMlO6zsQ': 'test'
}


def api_auth(username, password):
	if username in API_KEYS:
		return True
	return False

def basic_auth(auth):
	def decore(f):
		def _request_auth(handler):
			handler.set_header('WWW-Authenticate', 'Basic realm=JSL')
			handler.set_status(401)
			handler.finish()
			return False
		
		@functools.wraps(f)
		def new_f(*args):
			handler = args[0]
 
			auth_header = handler.request.headers.get('Authorization')
			if auth_header is None: 
				return _request_auth(handler)
			if not auth_header.startswith('Basic '): 
				return _request_auth(handler)
 
			auth_decoded = base64.decodestring(auth_header[6:])
			username, password = auth_decoded.split(':', 2)
 
			if (auth(username, password)):
				f(*args)
			else:
				_request_auth(handler)
					
		return new_f
	return decore


class ResHandler(tornado.web.RequestHandler):
	@basic_auth(api_auth)
	def get(self):
		self.write("hello")
app = tornado.web.Application([
	(r'/api/res/', ResHandler),
], **settings)

if __name__ == '__main__':
	import tornado.options
	tornado.options.parse_command_line()

	app.listen(9527)
	tornado.ioloop.IOLoop.instance().start()
