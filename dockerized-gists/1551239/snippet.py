# A base skeleton to simplify decorator implementations.
#
# All decorator classes needs only to extend this class by implementing the
# _init() and _call() methods and do not have to worry about the inconsistency
# of python decorators.
#
# _init: The method is called once when the decorator is created. The decorator
#        arguments, if any, will be passed on to this method.
# _call: Implements the function call, all arguments to the function will be
#        passed on to this method.
# _f:    The internal reference to the decorated method.
class Decorator(object):
    def __init__(self, *args, **kwargs):
        if len(args) == 1 and not kwargs and hasattr(args[0], '__call__'):
            # unargumented decorator
            self._f = args[0]
            self._init()
        else:
            # argumented decorator
            self._f = None
            self.__args = args
            self.__kwargs = kwargs
      
    def __call__(self, *args, **kwargs):
        if self._f:
            return self._call(*args, **kwargs)
        else:
            self._f = args[0]
            self._init(*self.__args, **self.__kwargs)
            return self
        
    def __get__(self, obj, ownerClass=None):
        return types.MethodType(self, obj)

    def __getattr__(self, *args, **kwargs):
        try:
            return self._f.__getattribute__(*args, **kwargs)
        except AttributeError:
            return self._f.__getattr__(*args, **kwargs)

    def _init(self, *args, **kwargs):
        # TODO stub to initialize the decorator
        pass
    
    def _call(self, *args, **kwargs):
        # TODO stub to implement function calls
        return self._f(*args, **kwargs)




### Example usage ###

class PrintDebugDecorator(Decorator):
    def _call(self, *args, **kwargs):
        print 'calling', self._f, 'with', args, 'and', kwargs
        return self._f(*args, **kwargs)

class ModuloDecorator(Decorator):
    def _init(self, n=None):
        self.__n = n if n else 42

    def _call(self, *args, **kwargs):
        return self._f(*args, **kwargs) % self.__n

@PrintDebugDecorator
def f(a, b, c=None):
    return c if c else a+b

@ModuloDecorator(2)
def g(a, b):
    return a + b

@ModuloDecorator
def h(a, b):
    return a + b