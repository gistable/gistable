from __future__ import unicode_literals
from wrapt import ObjectProxy

class Callable(ObjectProxy):
    def __call__(self, *args, **kwargs):
        result = self.__wrapped__
        if 'upper' in kwargs:
            result = result.upper()
        return result

class Test(object):
    __slots__ = ('name',)

    def __init__(self, name):
        self.name = name

    @property
    def fullname(self):
        return Callable(self.name)


test = Test(name='test')
assert test.fullname == 'test'
assert isinstance(test.fullname, unicode) is True
assert test.fullname(upper=True) == 'TEST'
assert test.fullname()[3] == 't'
