# Copyright (c) 2011 Phil Plante <unhappyrobot AT gmail DOT com>
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

import tornado.escape

class FlashMessageMixin(object):
	def set_flash_message(self, key, message):
		if not isinstance(message, basestring):
			message = tornado.escape.json_encode(message)
		
		self.set_secure_cookie('flash_msg_%s' % key, message)
	
	def get_flash_message(self, key):
		val = self.get_secure_cookie('flash_msg_%s' % key)
		self.clear_cookie('flash_msg_%s' % key)
		
		if val is not None:
			val = tornado.escape.json_decode(val)
		
		return val