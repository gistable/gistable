import functools

def decorator(d):
    "Make function d a decorator: d wraps a function fn."
    def _d(fn):
        return functools.update_wrapper(d(fn), fn)
    return _d
decorator = decorator(decorator)(decorator)

def decorator(annotation):
    "Make function d a decorator: d wraps a function fn."
    def inner_decorator(d):
        def _d(fn):
            f = functools.update_wrapper(d(fn), fn)
            f.__doc__ += ' (%s)' % annotation
            return f
        functools.update_wrapper(_d, d)
        return _d
    functools.update_wrapper(inner_decorator, decorator)
    return inner_decorator

def dec(d):
    "Make function d a decorator: d wraps a function fn."
    def _d(fn):
        return functools.update_wrapper(d(fn), fn)
    functools.update_wrapper(_d, d)
    return d    

@decorator('N-ary arguments allowed')
def n_ary(f):
    """Given binary function f(x, y), return an n_ary function such
    that f(x, y, z) = f(x, f(y,z)), etc. Also allow f(x) = x."""
    def n_ary_f(x, *args):
        return x if not args else f(x, n_ary_f(*args))
    return n_ary_f

@decorator('Memoized')
def memo(f):
    """Decorator that caches the return value for each call to f(args).
    Then when called again with same args, we can just look it up."""
    cache = {}
    def _f(*args):
        try:
            return cache[args]
        except KeyError:
            cache[args] = result = f(*args)
            return result
        except TypeError:
            # some element of args can't be a dict key
            return f(args)
    return _f

@decorator('# of calls counted')
def countcalls(f):
    "Decorator that makes the function count calls to it, in callcounts[f]."
    def _f(*args):
        callcounts[_f] += 1
        return f(*args)
    callcounts[_f] = 0
    return _f
callcounts = {}

@decorator('Step traced')
def trace(f):
    'trace the execution step'
    indent = '   '
    def _f(*args):
        signature = '%s(%s)' % (f.__name__, ', '.join(map(repr, args)))
        print '%s--> %s' % (trace.level*indent, signature)
        trace.level += 1
        try:
            result = f(*args)
            print '%s<-- %s == %s' % ((trace.level-1)*indent, 
                                      signature, result)
        finally:
            trace.level -= 1
        return result
    trace.level = 0
    return _f

def disabled(f):
    # Example: Use trace = disabled to turn off trace decorators
    return f

@trace
@memo
def fib(n):
    'compute nth fib number'
    if n == 0 or n == 1:
        return 1
    else:
        return fib(n-1) + fib(n-2)

if __name__ == '__main__':
    fib(6) #running this in the browser's IDE  will not display the indentations!