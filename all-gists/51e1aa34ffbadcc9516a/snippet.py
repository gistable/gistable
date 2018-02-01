# def bind(value, fn):
#     return fn(value)

# print bind ( 12, lambda x :
#       bind ( 13, lambda y :
#              lambda x,y :x+y))()

# def maybe_bind(value, fn) :
#     return fn(value) if value else None


class Identity(object):
    def __init__(self,val):
        self.value = val

    def bind(self, fn):
        return fn(self.value)
    
    @classmethod
    def unit(cls, value):
        return cls(value)

    def __str__(self):
        return "Identity:%s"%self.value
    
print Identity.unit(12).bind(lambda x :
                             Identity.unit(130).bind(lambda y : Identity.unit(x+y)))

print Identity(12).bind(lambda x :
      Identity(130).bind(lambda y : Identity.unit(x+y)))


class Maybe(object):
    def __init__(self, val):
        self.value = val

    def bind(self, fn):
        return fn(self.value) if self.value else Maybe(None)

    @classmethod
    def unit(cls, value):
        return cls(value)
    
    def __str__(self):
        return "Maybe:%s"%self.value

print Maybe(12).bind(lambda x :
      Maybe(None).bind( lambda y : Maybe.unit(x+y)))
print Maybe(12).bind(lambda x :
      Maybe(60).bind(lambda y : Maybe.unit(x+y)))
class ErrorM(object):
    def __init__(self, val,err=None):
        self.value = (val, err)
    @classmethod
    def unit(cls, value):
        return cls(value)
        
    def __str__(self):
        return "ErrorM:[%s,%s]"%self.value
    
    def bind(self, fn):
        val, error = self.value
        if error:
            return ErrorM(*self.value)
        
        try: 
            return fn(val)
        except Exception as e:
            return ErrorM(None, e)

# x -> Mx
def dividor(a,b):
    return ErrorM.unit(a/b)
    
print ErrorM(12).bind(lambda x :
      ErrorM(2).bind(lambda y :
      dividor(x,y)))

print ErrorM(12).bind(lambda x :
      ErrorM(0).bind(lambda y :
      dividor(x,y)))


# stephan@hackit01:~/source/py$ python monads.py 
# Identity:142
# Identity:142
# Maybe:None
# Maybe:72
# ErrorM:[6,None]
# ErrorM:[None,integer division or modulo by zero]
