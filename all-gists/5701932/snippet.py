import sys


class EnumType(type):

    @staticmethod
    def __prepare__(name, bases, **kwargs):
        rv = {}
        rv['max_val'] = 0
        def iota():
            rv['max_val'] += 1
            return rv['max_val']
        rv['iota'] = iota
        return rv

    def __new__(cls, name, bases, d):
        d['__slots__'] = ()
        rv = type.__new__(cls, name, bases, d)
        reverse_mapping = dict(getattr(rv, '__values__', None) or {})
        for key, value in d.items():
            if isinstance(value, int):
                val = rv(value)
                setattr(rv, key, val)
                reverse_mapping[val] = key
        rv.__values__ = reverse_mapping
        return rv


class Enum(int, metaclass=EnumType):
    __slots__ = ()

    def __str__(self):
        return '%s.%s' % (
            self.__class__.__name__,
            self.__class__.__values__[self]
        )

    def __repr__(self):
        return str(self)


class Colors(Enum):
    red = iota()
    blue = iota()
    green = iota()


print(Colors.red)
