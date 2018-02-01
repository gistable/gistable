import unittest
class StepCollection(object):
	def __setattr__(self, attr, val):
		if hasattr(self, attr):
			raise RuntimeError("step %s is already declared!" % (attr,))
		return super(StepCollection, self).__setattr__(attr, val)

class Object(object): pass
class World(unittest.TestCase):
	def __init__(self):
		self._reset()

	def __getattr__(self, a):
		return getattr(self._current, a)

	def _reset(self):
		self._current = Object()

class StepCollectionWrapper(object):
	def __init__(self, prefix):
		self._prefix = prefix

	def __getattr__(self, a):
		attr = getattr(steps, a)
		return attr(self._prefix)

steps = StepCollection()
world = World()
Given = StepCollectionWrapper('Given')
When = StepCollectionWrapper('When')
Then = StepCollectionWrapper('Then')
And = StepCollectionWrapper('And')

class TestCase(unittest.TestCase):
	def setUp(self):
		global world
		world._reset()

import functools
import sys
import termstyle
def step(func):
	name = func.__name__.replace('_', ' ')
	def _(prefix):
		@functools.wraps(func)
		def s(*a, **kw):
			desc = "\t%s %s" % (prefix, ' '.join([
					name,
					termstyle.bold(' '.join(map(repr,a))),
					' '.join(["%s=%r" % (k, termstyle.bold(v)) for k,v in kw.items()])])
			)
			try:
				ret = func(*a, **kw)
				print >> sys.stderr, termstyle.green(desc)
				return ret
			except:
				print >> sys.stderr, termstyle.red(desc)
				import traceback
				traceback.print_exc(file=sys.stderr)
				raise
		return s

	setattr(steps, func.__name__, _)
	return func
