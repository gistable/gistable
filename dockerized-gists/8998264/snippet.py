from functools import wraps
import inspect


def typechecked(func):
    argspec = inspect.getfullargspec(func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        for i, (arg, argname) in enumerate(zip(args, argspec.args)):
            type_ = argspec.annotations.get(argname)
            if type_ and not isinstance(args[i], type_):
                raise TypeError('Expected {!r} for argument "{}", got {!r} instead'.format(type_, argname, type(arg)))
        for argname, arg in kwargs.items():
            type_ = argspec.annotations.get(argname)
            if type_ and not isinstance(arg, type_):
                raise TypeError('Expected {!r} for argument "{}", got {!r} instead'.format(type_, argname, type(arg)))
        return func(*args, **kwargs)
    return wrapper