import copy

class gloss(dict):
    """
    A dictionary like object that supports attribute access, too.
    
    >>> import pickle

    >>> s = gloss(a=123)
    >>> c = s.copy()

    >>> s
    {'a': 123}
    >>> s['a']
    123
    >>> s.a
    123
    >>> c
    {'a': 123}

    >>> c.b = 456
    >>> s
    {'a': 123}
    >>> c
    {'a': 123, 'b': 456}

    >>> s = gloss()
    >>> s.l = [4, 5, 6]
    >>> s.l
    [4, 5, 6]

    >>> c = s.copy()
    >>> c.l
    [4, 5, 6]
    >>> c.l[1] = 'X'
    >>> c.l
    [4, 'X', 6]
    >>> s.l
    [4, 5, 6]

    >>> dir(s)
    ['l']
    >>> c.t = (7, 8, 9)
    >>> dir(c)
    ['l', 't']

    >>> x = pickle.dumps(s)
    >>> pickle.loads(x)
    {'l': [4, 5, 6]}
    >>> gloss(s)
    {'l': [4, 5, 6]}
    >>> gloss(s, v=1)
    {'l': [4, 5, 6], 'v': 1}

    """
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def __getitem__(self, name):
        return super(gloss, self).__getitem__(name)

    def __setitem__(self, key, value):
        return super(gloss, self).__setitem__(key, value)

    def __getstate__(self):
        return self.items()

    def __setstate__(self, items):
        for key, val in items:
            self.__dict__[key] = val

    def __dir__(self):
        return self.keys()

    @property
    def __members__(self):
        return self.__dir__()

    __getattr__ = __getitem__
    __setattr__ = __setitem__
    __call__ = __getitem__

    def copy(self):
        new = gloss()
        for key, val in self.__getstate__():
            new[key] = copy.copy(val)
        return new

if __name__ == "__main__":
    import doctest
    doctest.testmod()
