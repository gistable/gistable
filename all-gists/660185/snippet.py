def authenticated(auth):
	
	def decore(f):

		def _request_auth(handler):
			handler.set_header('WWW-Authenticate', 'Basic realm=tmr')
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
				f(*args, username=username)
			else:
				_request_auth(handler)
					
		return new_f
	return decore