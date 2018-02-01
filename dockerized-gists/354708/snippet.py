# -*- coding: utf-8 -*-

import tornado.web
import tornado.httpserver
import tornado.ioloop

class PageHandler(tornado.web.RequestHandler):
	def get(self,page_id = 'save'):
		self.write("<html><head></head><body><form method='post' action='/page/"+str(page_id)+"'><input type='text' name='ola'/></form></body></html>");
	def post(self,page_id = 'save'):
		self.write(page_id)

handlers = [
	(r"/page/([0-9]+)", PageHandler),
	(r"/page/save", PageHandler)
]

app = tornado.web.Application(handlers)

http_server = tornado.httpserver.HTTPServer(app);
http_server.listen(80)

tornado.ioloop.IOLoop.instance().start()

