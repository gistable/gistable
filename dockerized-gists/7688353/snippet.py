#!/usr/bin/python3
# coding: utf8
# Should work in both Python 2 and Python 3
from __future__ import unicode_literals
from __future__ import print_function

import io

def iterable_to_stream(iterable, buffer_size=io.DEFAULT_BUFFER_SIZE):
	"""
	Lets you use an iterable (e.g. a generator) that yields bytestrings as a read-only input stream.
	
	The stream implements Python 3's newer I/O API (available in Python 2's io module).
	For efficiency, the stream is buffered.
	"""
	class IterStream(io.RawIOBase):
		def __init__(self):
			self.leftover = None
		def readable(self):
			return True
		def readinto(self, b):
			try:
				l = len(b)	# We're supposed to return at most this much
				chunk = self.leftover or next(iterable)
				output, self.leftover = chunk[:l], chunk[l:]
				b[:len(output)] = output
				return len(output)
			except StopIteration:
				return 0	# indicate EOF
	return io.BufferedReader(IterStream(), buffer_size=buffer_size)

if __name__ == '__main__':
	# Example
	with iterable_to_stream(str(x**2).encode('utf8') for x in range(11)) as s:
		print(s.read())