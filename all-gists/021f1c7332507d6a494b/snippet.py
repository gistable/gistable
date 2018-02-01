#!/usr/bin/env python


def curry(func):
    """
    Decorator to curry a function, typical usage:

    >>> @curry
    ... def foo(a, b, c):
    ...    return a + b + c

    The function still work normally:
    >>> foo(1, 2, 3)
    6

    And in various curried forms:
    >>> foo(1)(2, 3)
    6
    >>> foo(1)(2)(3)
    6

    This also work with named arguments:
    >>> foo(a=1)(b=2)(c=3)
    6
    >>> foo(b=1)(c=2)(a=3)
    6
    >>> foo(a=1, b=2)(c=3)
    6
    >>> foo(a=1)(b=2, c=3)
    6

    And you may also change your mind on named arguments,
    But I don't know why you may want to do that:
    >>> foo(a=1, b=0)(b=2, c=3)
    6

    Finally, if you give more parameters than expected, the exception
    is the expected one, not some garbage produced by the currying
    mechanism:

    >>> foo(1, 2)(3, 4)
    Traceback (most recent call last):
       ...
    TypeError: foo() takes exactly 3 arguments (4 given)
    """
    def curried(*args, **kwargs):
        if len(args) + len(kwargs) >= func.__code__.co_argcount:
            return func(*args, **kwargs)
        return (lambda *args2, **kwargs2:
                curried(*(args + args2), **dict(kwargs, **kwargs2)))
    return curried


if __name__ == "__main__":
    import doctest
    doctest.testmod()
