# import hook (sys.meta_path) for mocking imports
# using mock library (http://www.voidspace.org.uk/python/mock/)
#

import sys
import mock
import logging

IMPORTER = None
MOCK = None

class MockImporter(object):
   def __init__(self, mockparent):
      self.mock = mockparent
      self.enabled = True
   def install(self):
      if self not in sys.meta_path:
         sys.meta_path.append(self)
   def enable(self):
      self.enabled = True
   def disable(self):
      self.enabled = False
   def find_module(self, fullname, path=None):
      if not self.enabled:
         raise ImportError('mockimporter disabled')
      logging.debug('find_module: %s, %s', fullname, path)
      return self
   def load_module(self, fullname):
      logging.debug('load_module', fullname)
      mod = self.mock
      for path in fullname.split('.'):
         mod = getattr(mod, path)
         mod.__path__ = []
         mod.__file__ = "<%s>" % self.__class__.__name__
         mod.__loader__ = self
      mod = sys.modules.setdefault(fullname, mod)
      # sys.modules[fullname] = mod
      return mod

def install():
   global MOCK
   global IMPORTER
   if MOCK is None:
      MOCK = mock.Mock()
   if IMPORTER is None:
      IMPORTER = MockImporter(MOCK)
   IMPORTER.install()

def enable():
   if IMPORTER is not None:
      IMPORTER.enable()

def disable():
   if IMPORTER is not None:
      IMPORTER.disable()
