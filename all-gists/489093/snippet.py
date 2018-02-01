# Copyright (c) 2010, Philip Plante of EndlessPaths.com
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import logging
import shlex
import subprocess
import tornado

class AsyncProcessMixIn(tornado.web.RequestHandler):
	"""
	class SampleHandler(AsyncProcessMixIn):
		@tornado.web.asynchronous
		def get(self):
			self.call_subprocess('ls /', self.on_ls)
		
		def on_ls(self, output, return_code):
			self.write("return code is: %d" % (return_code,))
			self.write("output is:\n%s" % (output.read(),)) # output is a file-like object returned by subprocess.Popen
			
			self.finish()
	
	"""
	def call_subprocess(self, command, callback=None):
		self.ioloop = tornado.ioloop.IOLoop.instance()
		self.pipe = p = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
		self.ioloop.add_handler(p.stdout.fileno(), self.async_callback(self.on_subprocess_result, callback), self.ioloop.READ)
	
	def on_subprocess_result(self, callback, fd, result):
		try:
			if callback:
				callback(self.pipe.stdout)
		except Exception, e:
			logging.error(e)
		finally:
			self.ioloop.remove_handler(fd)