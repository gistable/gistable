#-*- coding:utf-8 -*- 
import Queue
from contextlib import contextmanager

class ObjectPool(object):
  """A simple object pool with thread safe"""
  def __init__(self,objectFn,*args,**kwargs):
    super(ObjectPool, self).__init__()
    self.objectFn = objectFn
    self.objectCls = None
    self._myInit(*args,**kwargs)
  
  def __init__(self,objectCls,*args,**kwargs):
    super(ObjectPool, self).__init__()
    self.objectCls = objectCls
    self.objectFn = None
    self._myInit(*args,**kwargs)
    
  def _myInit(self,*args,**kwargs):
    self.args = args
    self.maxSize = int(kwargs.get("maxSize",1))
    self.queue = Queue.Queue()
  def _getObj(self):
    if self.objectFn:
      return objectFn(self.args)
    else:
      return apply(self.objectCls, self.args)
  
  def borrowObj(self):
    if self.queue.qsize()<self.maxSize and self.queue.empty():
      self.queue.put(self._getObj())
    return self.queue.get()
  
  def returnObj(self,obj):
    self.queue.put(obj)
    
@contextmanager
def poolObj(pool):
  obj = pool.borrowObj()
  try:
    yield obj
  except Exception, e:
    yield None
    raise e
  finally:
    pool.returnObj(obj)