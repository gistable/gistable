''''
From http://code.activestate.com/recipes/363602-lazy-property-evaluation/

Usage:

class MyClass():
    @lazyloaded
    def config(self):
        return {'yay': 'nay'}

foo = MyClass()
print foo.config['yay']
''''

class lazyloaded(object):
    '''Allows one to wrap a method call so that the first call lazy loads the data
    This only works for class methods
    '''
    
    def __init__(self, func):
        self._func = func

    def __get__(self, obj, _=None):
        if obj is None:
            return self
        value = self._func(obj)
        setattr(obj, self._func.func_name, value)
        return value
