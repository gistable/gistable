import types

class decorator(object):
    """
    When using a decorator, the function that is being decorated
    loses its __name__, docstring, and signature.

    For example, consider the generic decorator ``my_decorator``:

        def my_decorator(fn):
            def wrapped(*args, **kwargs):
                print 'Calling', fn.__name__
                result = fn(*args, **kwargs)
                print 'Done with', fn__name__
                return result
            return wrapped

    and the decorated function ``my_function``:

        @my_decorator
        def my_function(a, b, c, d):
            pass

    Preserving the function's __name__ and docstring are simple enough
    either by outright copying or using the helper function ``functools.wraps``,
    however, ``my_function``'s signature will remain the same as ``wrapped``:
    ``*args, **kwargs``. This isn't a that big of a problem until introspection
    is needed.

    Python classes are capable of being used as decorators, however,
    whenever a class is used as a decorator, the function actually
    becomes an instance of that class. Again this is a problem
    for introspection.

    The "solution" is to make the class look completely like the function

    Using this class as a standalone decorator acts as an identity function.
    To get the most use, this should be subclassed. When calling the decorated
    function, several things occur:

    1. The ``__call__`` method is invoked.
    1. The ``*args`` and ``**kwargs`` get set as attributes of the instance.
    1. The ``before_call`` method is invoked.
    1. ``self.function`` is called with ``*args`` and ``**kwargs`` and
       the result is stored in ``self.result``.
    1. The ``after_call`` method is invoked.
    1. The result in ``self.result`` is returned.

    It is intended that only ``before_call`` and ``after_call`` are to be
    overridden in subclasses.

    :param fn: the function to decorate
    :type fn: function
    """
    def __getattribute__(self, name):
        if name == '__class__':
            # calling type(decorator()) will return <type 'function'>
            # this is used to trick the inspect module >:)
            return types.FunctionType
        return super(decorator, self).__getattribute__(name)

    def __init__(self, fn):
        # let's pretend for just a second that this class
        # is actually a function. Explicity copying the attributes
        # allows for stacked decorators.
        self.__call__ = fn.__call__
        self.__closure__ = fn.__closure__
        self.__code__ = fn.__code__
        self.__doc__ = fn.__doc__
        self.__name__ = fn.__name__
        self.__defaults__ = fn.__defaults__
        self.func_defaults = fn.func_defaults
        self.func_closure = fn.func_closure
        self.func_code = fn.func_code
        self.func_dict = fn.func_dict
        self.func_doc = fn.func_doc
        self.func_globals = fn.func_globals
        self.func_name = fn.func_name
        # any attributes that need to be added should be added
        # *after* converting the class to a function
        self.args = None
        self.kwargs = None
        self.result = None
        self.function = fn

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        self.before_call()
        self.result = self.function(*args, **kwargs)
        self.after_call()

        return self.result

    def before_call(self):
        pass

    def after_call(self):
        pass