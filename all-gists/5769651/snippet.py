# From http://stackoverflow.com/a/1914798/711380
class _PickleableStaticMethod(object):
    def __init__(self, fn, cls=None):
        self.cls = cls
        self.fn = fn
    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)
    def __get__(self, obj, cls):
        return _PickleableStaticMethod(self.fn, cls)
    def __getstate__(self):
        return (self.cls, self.fn.__name__)
    def __setstate__(self, state):
        self.cls, name = state
        self.fn = getattr(self.cls, name).fn


class pickleable_staticmethods(type):
    def __new__(cls, name, bases, dct):
        new_cls = type.__new__(cls, name, bases, dct)
        dct = new_cls.__dict__
        for name in dct.keys():
            value = new_cls.__dict__[name]
            if isinstance(value, staticmethod):
                setattr(
                        new_cls,
                        name,
                        _PickleableStaticMethod(value.__get__(None, new_cls),
                                               new_cls))
        return new_cls


###############################################################################

import unittest


class Test_picklethis1(object):
    __metaclass__ = pickleable_staticmethods

class Test_picklethis2(Test_picklethis1):
    @staticmethod
    def foo():
        return 42

class Test_pickle_staticmethod(unittest.TestCase):
    def test_pickle(self):
        import pickle
        d = pickle.dumps(Test_picklethis2.foo)
        try:
            f = pickle.loads(d)
        except pickle.PicklingError, e:
            self.fail("PicklingError was raised:\n%r" % e)
        self.assertEqual(f(), 42)


if __name__ == '__main__':
    unittest.main()
