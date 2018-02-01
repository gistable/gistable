import time


def cooldown(time):
    """Decorate a method with a cooldown.
    
    Prevents a method from being called twice
    within ``time`` seconds by the same instance.
    
    :param float time:
        Minimum time in seconds allowed between two method calls
    """
    def decorator(method):
        return _UnboundCooldownMethod(method, time)
    return decorator


class _UnboundCooldownMethod:
    """A wrapper around an unbound method for adding a cooldown.
    
    This class is used to replace methods in classes with
    an object that stores the original method and a cooldown,
    then uses `__get__` to bind the objects accessing the method
    to their bound methods.
    """

    def __init__(self, method, cooldown):
        """Initialize a new unbound cooldown method.
        
        :param callable method:
            Method to wrap around
        :param float cooldown:
            The cooldown between two function calls
        """
        self.method = method
        self.cooldown = cooldown
        self._bindings = {}

    def __get__(self, obj, type_):
        """Bind the accessing instance to a method.
        
        Whenever this object is accessed through an instance
        rather than through the class, this will bind the
        instance to a method and return a ``_BoundCooldownMethod``
        which will handle the calling.
        
        :returns _BoundCooldownMethod:
            An object for handling the calling of the method
        """
        if obj is None:
            return self
        if id(obj) not in self._bindings:
            bound_method = self.method.__get__(obj)
            self._bindings[id(obj)] = _BoundCooldownMethod(bound_method, self.cooldown)
        return self._bindings[id(obj)]


class _BoundCooldownMethod:
    """A cooldown method which handles the calling.
    
    Stores the bound method and handles the cooldown
    for an object, making sure the bound method is not
    called too often.
    """

    def __init__(self, method, cooldown):
        """Initialize the bound cooldown method.
        
        :param callable method:
            The bound method
        :param float cooldown:
            Time between method calls
        """
        self.method = method
        self.cooldown = cooldown
        self._last_call_time = 0

    @property
    def remaining_cooldown(self):
        """Time until the cooldown ends."""
        time_delta = time.time() - self._last_call_time
        return max(0, self.cooldown - time_delta)

    def __call__(self, *args, **kwargs):
        """Call the bound method if cooldown has hit zero."""
        if self.remaining_cooldown == 0:
            self._last_call_time = time.time()
            return self.method(*args, **kwargs)
