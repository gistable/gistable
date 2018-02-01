from functools import wraps 

def add_section(punctuation):
    def wrapper(func):
		@wraps(func)
		def inner(msg):
			print punctuation*len(msg)
			func(msg)
			print punctuation*len(msg)
		return inner
	return wrapper

@add_section('#')
def display(msg):
	print msg