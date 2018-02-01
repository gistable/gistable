class with_request_context(object):

	def __init__(self, f, app=None, request=None):
		self.f = f
		if app:
			self.app = app
		else:
			self.app = www
		if request:
			self.request = request
		else:
			self.request = '/'
		self.__name__ = f.__name__ + 'with_request_context'

	def __call__(self, *args):
		with self.app.test_request_context(self.request):
			return self.f(*args)