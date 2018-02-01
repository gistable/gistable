class TailPromise(object):
  __metaclass__ = PromiseMetaClass

  def __init__(self,func,args,kw):
    self.__func = func
    self.__args = args
    self.__kw = kw

  def __arginfo__(self):
    return self.__args, self.__kw

  def __func__(self):
    return self.__func
  
  def __force__(self):
    return self.__func(*self.__args,**self.__kw)

def trampolined(g):

  def func(*args,**kwargs):
    old_trampolining = func.currently_trampolining

    # if this is not the first call, and it is a tail call:
    if (func.currently_trampolining != func):
      # Set up the trampoline!
      func.currently_trampolining = func
      while 1:
        res = g(*args,**kwargs)
	if res.__class__ is TailPromise and res.__func__() is g:
          # A tail recursion!
          args,kwargs = res.__arginfo__()
        else:
          func.currently_trampolining = old_trampolining
	  return res
    else:
      return TailPromise(g,args,kwargs)

  func.currently_trampolining = None
  return func