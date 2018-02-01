#!/usr/bin/env python3.0
import sys
import multiprocessing

def process(function, name=None):
	"""Decorates a into spawning a new process. Yay clarity."""
	
	def decorated(*args, *kwargs):
		p = multiprocessing.Process(target=function, name=name, args=args, kwargs=kwargs)
		p.start()
		return(p)
	
	return(decorated)

def main(*args):
	print("Hello, world!")

if __name__ == "__main__": sys.exit(main(*sys.argv[1:]))
