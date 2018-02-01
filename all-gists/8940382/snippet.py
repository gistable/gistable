from functools import partial


class partialmethod(partial):
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return partial(self.func, instance,
                       *(self.args or ()), **(self.keywords or {}))


# Example usage:

class C(object):
    def __init__(self, m):
        self.m = m
    
    def foo(self, x, y):
        return self.m * (x + y)
    
    bar = partialmethod(foo, 1)

c = C(2)
assert c.foo(1, 2) == 6
assert c.bar(3) == 8

