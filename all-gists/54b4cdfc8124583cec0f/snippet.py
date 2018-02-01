class NestMeta(type):
    def __getattr__(cls, key):
        return cls(cls, key)

    def __str__(cls):
        return cls.__name__

    __repr__ = __str__


class Nest(object):
    __metaclass__ = NestMeta

    parent = None
    name = None

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

        self.args = []
        self.kwargs = {}

    def __str__(self):
        base = '' if self.parent is None else str(self.parent)

        parts = [self.name]
        parts.extend(str(item) for item in self.args)
        parts.extend('{}={}'.format(key, str(value)) for key, value in self.kwargs.iteritems())

        return '{}/{}'.format(base, '.'.join(parts))

    __repr__ = __str__

    def __call__(self, *args, **kwargs):
        self.args.extend(args)
        self.kwargs.update(kwargs)

        return self

    def __getattr__(self, key):
        return self.__class__(self, key)
