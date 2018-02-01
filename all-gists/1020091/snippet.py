# encoding: utf-8

class DotDict(dict):

    def __init__(self, *a, **kw):
        dict.__init__(self, *a, **kw)
        for key in self:
            self._validate_key(key)

    def _validate_key(self, key):
        try:
            class IsIdentifier(object): __slots__ = key
        except TypeError:
            raise TypeError("invalid identifier: '%s'" % key)

        try:
            dict.__getattribute__(self, key)
        except AttributeError:
            pass
        else:
            raise TypeError("builtin dict attribute: '%s'" % key)

    def __getattribute__(self, name):
        try:
            return dict.__getattribute__(self, name)
        except AttributeError:
            if name in self:
                return self[name]
            raise

    def __setitem__(self, key, value):
        self._validate_key(key)
        dict.__setitem__(self, key, value)

    __setattr__ = __setitem__

    __delattr__ = dict.__delitem__

    def copy(self, *a, **kw):
        obj = dict.copy(self, *a, **kw)
        if obj.__class__ is DotDict.__class__:
            return obj
        return DotDict(obj)

    @classmethod
    def fromkeys(cls, *a, **kw):
        obj = super(DotDict, cls).fromkeys(*a, **kw)
        if obj.__class__ is DotDict.__class__:
            return obj
        return cls(obj)
