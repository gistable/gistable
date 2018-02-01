from functools import wraps


def skip_when_testing(func=None):
	"""
	Provides a way to provide functionality that only applies in the real production environment, otherwise stubs out the function.
	
	Use this with **care** as this makes testability difficult and can lead to errors/bugs leaking into production.  This should really only be used for non-functional (fire-and-forget) components like error logging or analytics.
	"""
	def wrapper(func):
		@wraps(func)
		def wrapped(*args, **kwargs):
			import sys
			# Look for harvest or test for testing environments
			if set(('test', 'harvest')) & set(sys.argv):
				return
			# Also break if we're running within nose
			for arg in sys.argv:
				if 'nosetests' in arg:
					return
			return func(*args, **kwargs)
		return wrapped
	if func:
		return wrapper(func)
	else:
		return wrapper
