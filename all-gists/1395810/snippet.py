import functools
import logging
from google.appengine.api import memcache
 
def cached(time=1200):
  """
  Decorator that caches the result of a method for the specified time in seconds.
  
  Use it as:
    
    @cached(time=1200)
    def functionToCache(arguments):
      ...
    
  """
  def decorator(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
      key = '%s%s%s' % (function.__name__, str(args), str(kwargs))
      value = memcache.get(key)
      logging.debug('Cache lookup for %s, found? %s', key, value != None)
      if not value:
        value = function(*args, **kwargs)
        memcache.set(key, value, time=time)
      return value
    return wrapper
  return decorator