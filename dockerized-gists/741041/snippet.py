import functools
import logging
import sys

class ResultCollector(object):
  '''Like a BarrierCallback, but saves results passed to the callback.

  >>> rc = ResultCollector()
  >>> cb_foo = rc.get_callback('foo')
  >>> cb_bar = rc.get_callback('bar')
  >>> rc.when_done(lambda res: sys.stdout.write(sorted(res.items())))
  >>> cb_bar(1)
  >>> cb_foo(2)
  [('bar', 1), ('foo', 2)]
  '''
  def __init__(self):
    self.__results = {}
    self.__pending = 0
    self.__callback = None

  def get_callback(self, key):
    '''Returns a callback which takes one argument and saves it in the
    results under 'key'.
    '''
    assert self.__callback is None
    self.__pending += 1
    return functools.partial(self.__item_callback, key)

  def when_done(self, callback):
    '''Invokes the callback after all existing get_callback() functions
    have been called.  The callback will be passed one parameter,
    the dictionary of arguments to the get_callback() functions.
    '''
    assert self.__callback is None
    self.__callback = callback
    self.__maybe_call_callback()

  def __item_callback(self, key, value):
    if key in self.__results:
      logging.error("Multiple callbacks received for key %r.  Values: %r, %r",
                    key, self.__results[key], value)
      return
    self.__results[key] = value
    self.__pending -= 1
    self.__maybe_call_callback()

  def __maybe_call_callback(self):
    if self.__pending < 1 and self.__callback:
      self.__callback(self.__results)
      self.__callback = None
