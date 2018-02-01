'''
A simple wrapper make a class become a functor,
the class need a __call__ function. The (*sub,
**kwargs) will be passed for the __init__ function,
and the name of class will be the name of function
object.

Example
-------
@functor(*sub, **kwargs)
class functor_name(object):
    def __init__(self, *sub, **kwargs):
        ...
    def __call__(self):
        ...

Then you may use functor_name as a function.
'''
import sys


def functor(*sub, **kwargs):
    def wrapper(cls):
        module = sys.modules[cls.__module__]
        obj = cls(*sub, **kwargs)
        setattr(module, cls.__name__, obj)
        return obj
    return wrapper