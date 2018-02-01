class CachedProperty(object):
    """
    A cached property; A bit specific, as
    it runs the getter as an instance method
    & forwards the instance & init args to it.
    Uses python descriptors protocol
    """
    def __init__(self, getter, *args):
        self.getter = getter
        self.args = args or None

    def __get__(self, instance, owner):
        # If we don't have cache, go ahead and call the getter & cache its result
        if not hasattr(self, '_cache'):
            # This is the expensive getter call; The getter is provided with instance & optional args
            result = self.getter(instance, *self.args) if self.args is not None else self.getter(instance)
            # Cache the result in self
            setattr(self, '_cache', result)
        # We always return our cache
        return getattr(self, '_cache')

    def __set__(self, instance, value):
        # Set the new value to the cache
        setattr(self, '_cache', value)

    def __delete__(self, instance):
        # Remove cache
        delattr(self, '_cache')


# USAGE

class SomeClass(object):
    A, B, C = 1, 2, 3
    
    def __init__(self, *args, **kwargs):
        self.args = args or ()
        self.kwargs = kwargs or {}
        
    def has_arg(self, arg):
        return arg in self.args
    
    def expensive_getter_fn(x)
        # An expensive computation here
        return x
        
    # Typical usage case: expensive getter & some args for it to receive
    my_cached_prop_a = CachedProperty(expensive_getter_fn, SomeClass.A)
    my_cached_prop_b = CachedProperty(expensive_getter_fn, SomeClass.B)
    my_cached_prop_c = CachedProperty(expensive_getter_fn, SomeClass.C)
    
    # Another way to use it: lambda getter that invokes some instance method
    my_cached_prop_d = CachedProperty(lambda instance, arg: instance.has_arg, "some_arg")

