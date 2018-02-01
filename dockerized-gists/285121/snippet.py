import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

class BaseHandler(tornado.web.RequestHandler):
	pass
	
class HandlerMixin(object):
	listeners = []
	
	def add_listener(self, callback):
		handler = HandlerMixin
		handler.listeners.append(callback)
		print 'Total listeners: %i' % len(handler.listeners)
		
	def send_message(self, message):
		handler = HandlerMixin
		print 'Sending messages to %i listeners' % len(handler.listeners)
		for listener in handler.listeners:
			listener(message)
		handler.listeners = []
	
class MainHandler(BaseHandler, HandlerMixin):
	@tornado.web.asynchronous
	def get(self):
		self.add_listener(self.async_callback(self._callback))
		
	def _callback(self, message):
		if self.request.connection.stream.closed():
			return
		self.finish(message)
		
class MessageHandler(BaseHandler, HandlerMixin):
	def get(self):
		self.write('''
		<form method="post">
			<input type="text" name="message" />
			<input type="submit" />
		</form>
		''')
		
	def post(self):
		message = self.get_argument('message', None)
		self.send_message(message)
		self.redirect(self.request.uri)

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			(r'/', MainHandler),
			(r'/post/?', MessageHandler),
		]
		settings = dict()
		tornado.web.Application.__init__(self, handlers, **settings)

def main():
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(8888)
	tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
	main()