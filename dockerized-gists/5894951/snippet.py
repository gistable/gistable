#!/usr/bin/env python
"""
Decorator for fluent interface classes.
"""
import functools
import inspect


def chained(method):
    """Method decorator to allow chaining."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        return self if result is None else result
    return wrapper


def fluent(cls):
    """Class decorator to allow method chaining."""
    for name, member in cls.__dict__.iteritems():
        if inspect.isfunction(member):
            setattr(cls, name, chained(member))
    return cls


if __name__ == '__main__':
    class Foo(object):
        @chained
        def set_value(self, value):
            self.value = value

        def get_value(self):
            return self.value

    @fluent
    class Bar(object):
        def set_value(self, value):
            self.value = value
        
        def get_value(self):
            return self.value

    print Foo().set_value("Foo").get_value()
    print Bar().set_value("Bar").get_value()
