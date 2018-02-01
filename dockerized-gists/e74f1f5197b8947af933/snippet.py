from functools import wraps


def defaults(method='__init__', **default_args):
    """Class decorator.  Overrides method default arguments."""

    def decorate(cls):
        func = getattr(cls, method)

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            default_args.update(kwargs)
            return func(self, *args, **default_args)

        setattr(cls, method, wrapper)
        return cls

    return decorate