import ast
import random

class MaybeType(type):
  
  def __repr__(cls):
    return str(bool(random.randint(0, 1)))
    
  def __nonzero__(cls):
    return ast.literal_eval(repr(cls))
    
class Maybe(object):
  
  __metaclass__ = MaybeType
  
>>> Maybe
True
>>> Maybe
True
>>> Maybe
False
>>> bool(Maybe)
False
>>> bool(Maybe)
True
>>> True = Maybe  # import chaos
>>> True
True
>>> True
True
>>> True
False