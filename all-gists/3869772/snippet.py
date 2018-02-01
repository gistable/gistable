class Field(object):

    def __init__(self, default=None):
        self.val = default

    def __get__(self, obj, objtype):
        if obj is None:
            return self.__class__
        else:
            return self.val

    def __set__(self, obj, val):
        self.val = val


class ModelMeta(type):
    def __new__(cls, name, bases, dct):
        def __init__(self, **kwargs):
            for name, value in kwargs.items():
                if name in dct and isinstance(dct[name], Field):
                    setattr(self, name, value)
        dct['__init__'] = __init__
        return super(ModelMeta, cls).__new__(cls, name, bases, dct)


class Model(object):
    __metaclass__ = ModelMeta


class PositiveIntegerField(Field):

    def __init__(self, default=0):
        self.val = default

    def __set__(self, obj, val):
        if not isinstance(val, int):
            raise ValueError('Somente valores inteiros')
        if val < 0:
            raise ValueError('Somente valores > 0')
        self.val = val


class CharField(Field):

    def __init__(self, default=''):
        self.val = default

    def __set__(self, obj, val):
        if not isinstance(val, basestring):
            raise ValueError('Somente str ou unicode')
        self.val = val


class Download(Model):
    """
    >>> print Download.clicks
    <class '__main__.PositiveIntegerField'>
    >>> print Download.url
    <class '__main__.CharField'>
    >>> d = Download()
    >>> d.clicks = 1
    >>> d.url = 'http://pylestras.org'
    >>> print d.clicks
    1
    >>> print d.url
    http://pylestras.org
    >>> d2 = Download(clicks=1, url='http://google.com')
    >>> print d2.clicks
    1
    >>> print d2.url
    http://google.com
    >>> d3 = Download(clicks=-12, url='http://google.com')
    Traceback (most recent call last):
        ...
    ValueError: Somente valores > 0
    >>> d4 = Download(clicks=12, url=1234)
    Traceback (most recent call last):
        ...
    ValueError: Somente str ou unicode
    """

    clicks = PositiveIntegerField()
    url = CharField()


if __name__ == '__main__':
    import doctest
    doctest.testmod()