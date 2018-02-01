from inspect import getargspec
def curry(f, n=None):
    defaults = []
    if n == None:
        s = getargspec(f)
        n = len(s.args)
        if s.defaults:
            n -= len(s.defaults)
            defaults = zip(reversed(s.args),reversed(s.defaults))
    def newfunc(*args, **kwargs):
        if len(args) >= n:
            return f(*args, **kwargs)
        def to_curry(*nargs, **nkwargs):
            return f(*(args+nargs), **dict(defaults+kwargs.items()+nkwargs.items()))
        return curry(to_curry, n-len(args))
    return newfunc

    
"""
>>> from curry import curry
>>> @curry
... def add3(a,b,c): return a+b+c
...
>>> add3(1,2,3)
6
>>> add3(1)(2,3)
6
>>> add3(1,2)(3)
6
>>> add2 = add3(100)
>>> add2(5,6)
111
>>> add1 = add2(3.14)
>>> add1(5)
108.14
>>> map(add1,range(5))
[103.14, 104.14, 105.14, 106.14, 107.14]
"""
