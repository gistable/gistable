# ~*~ coding:utf-8 ~*~
"""
=============================================
Support Increment and Decrement on Python
=============================================

>>> import inc_dec
>>> i = int(1)
>>> ++i
>>> print i
2

This code is imperfect, so when you use this module
you have to add "int" to integer literal.

This code inspired in

http://d.hatena.ne.jp/atsuoishimoto/20121024/1351008010

"""


def _bind_meta(int):
    def _(method):
        def __(self, *args, **kw):
            self._inc = False
            self._dec = False
            return getattr(int, method)(self._value, *args, **kw)
        return __

    def __meta(cls, basetypes, d):
        methods = dir(int)
        methods = (method for method in methods if method not in d)
        for method in methods:
            if method not in ['__new__',
                              '__getattr__', '__getattribute__',
                              '__setattr__', '__setattribute__',
                              '__delattr__']:
                d[method] = _(method)
        return type(cls, basetypes, d)
    return __meta
_meta = _bind_meta(int)


class IncDecInt(int):

    __metaclass__ = _meta

    def __init__(self, *args, **kw):
        super(IncDecInt, self).__init__(*args, **kw)
        self._value = self
        self._inc = False
        self._dec = False

    def __pos__(self):
        if self._inc:
            self._inc = False
            self._value += 1
            return self
        else:
            self._inc = True
            return self

    def __neg__(self):
        if self._dec:
            self._dec = False
            self._value -= 1
            return self
        else:
            self._dec = True
            return self

# override int type
import __builtin__
__builtin__.int = IncDecInt
try:
    __builtins__.int = IncDecInt
except AttributeError:
    pass
int = IncDecInt

if __name__ == '__main__':
    # work
    i = int(1)
    ++i
    print i
    --i
    print i
    ++i
    print i + i * 5

    # not work
    i = 1
    ++i
    print i
