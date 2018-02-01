from ansible import errors
from jinja2.filters import environmentfilter

class FilterModule(object):
    def filters(self):
        return {
            'iterable': self.iterable
        }
    def iterable(*args):
      try:
        iterator = iter(args[1])
      except TypeError:
        return False
      else:
        return True