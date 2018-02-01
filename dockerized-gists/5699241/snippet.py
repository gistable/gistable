import contextlib


pad = ''

@contextlib.contextmanager
def call():
    global pad
    pad += "  "
    yield
    pad = pad[:-2]


def DebugMt(name, bases, dct):
    import functools
    import types

    def make_method_wrapper(f):
        @functools.wraps(f)
        def nf(*args, **kwargs):
            print "%s%s(args=%r, kwargs=%r)" % (pad, f.__name__, args, kwargs)
            with call():
                return f(*args, **kwargs)
        return nf

    class staticmethod_wrapper(object):
        def __init__(self, sm):
            self.sm = sm
        def __get__(self, inst=None, owner=None):
            f = self.sm.__get__(inst, owner)
            @functools.wraps(f)
            def nf(*args, **kwargs):
                print "%s%s(args=%r, kwargs=%r)" % (pad,
                                                    f.__name__, args, kwargs)
                with call():
                    return f(*args, **kwargs)
            return nf

    new_dct = {}
    for n, f in dct.iteritems():
        if isinstance(f, types.FunctionType):
            new_dct[n] = make_method_wrapper(f)
        elif isinstance(f, staticmethod):
            new_dct[n] = staticmethod_wrapper(f)
        else:
            new_dct[n] = f

    return type(name, bases, new_dct)
