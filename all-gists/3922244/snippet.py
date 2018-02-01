import re

def re_sub(pattern, replacement, string):
	def _r(m):
		# Now this is ugly.
		# Python has a "feature" where unmatched groups return None
		# then re.sub chokes on this.
		# see http://bugs.python.org/issue1519638
		
		# this works around and hooks into the internal of the re module...

		# the match object is replaced with a wrapper that
		# returns "" instead of None for unmatched groups

		class _m():
			def __init__(self, m):
				self.m=m
				self.string=m.string
			def group(self, n):
				return m.group(n) or ""

		return re._expand(pattern, _m(m), replacement)
	
	return re.sub(pattern, _r, string)

print re_sub('(ab)|(a)', r'(1:\1 2:\2)', 'abc')
# prints '(1:ab 2:)c'

