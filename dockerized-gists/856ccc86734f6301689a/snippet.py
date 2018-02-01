import inspect

class Singleton(type):
    _instances = {}
    _init = {}

    def __init__(cls, name, bases, dct):
        cls._init[cls] = dct.get('__init__', None)

    def __call__(cls, *args, **kwargs):
        init = cls._init[cls]
        if init is not None:
            key = (cls, frozenset(
                    inspect.getcallargs(init, None, *args, **kwargs).items()))
        else:
            key = cls

        if key not in cls._instances:
            cls._instances[key] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[key]

def tests():
    class A(object):
        __metaclass__ = Singleton
        FOO = 'bar'

    assert A() is A()

    class B(object):
        __metaclass__ = Singleton
        def __init__(self, key):
            self.key = key
    assert B('key1') is B('key1')
    assert B('key1') is not B('key2')

    class C(object):
        __metaclass__ = Singleton
        def __init__(self, key=None):
            self.key = key

    assert C() is C()
    assert C() is C(None)
    assert C(None) is C(key=None)
    assert C() is C(key=None)
    assert C() is not C('key')
    assert C('key') is C('key')
    assert C('key') is C(key='key')
    assert C('key1') is not C(key='key2')
    assert C(key='key1') is not C(key='key2')

    class D(object):
        __metaclass__ = Singleton
        def __init__(self):
            pass

    class E(object):
        __metaclass__ = Singleton
        def __init__(self):
            pass

    assert D() is not E()
