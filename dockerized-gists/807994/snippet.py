try:
    from com.google.common.base import Function
except ImportError:
    Function = None

class _FunctionTemplate(object):
    def __init__(self, f):
        self._func = f

    def apply(self, *args):
        return self._func(*args)

    def __call__(self, *args):
        return self._func(*args)

_bases = (_FunctionTemplate,)
if Function:
    _bases += (Function,)

_Function = type('_Function', _bases, {})

def functionize(f):
    return _Function(f)

if __name__ == '__main__':
    @functionize
    def foo(k, v):
        print k, v
        
    foo('from python', 1)
    foo.apply('applied via interface', 2)
