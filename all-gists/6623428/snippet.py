## Update! Found an alternative approach that's concise and feels much more idiomatic

def compose (f, g):
    return lambda x: f(g(x))

def comp(*args):
    return reduce(compose, args[1:], args[0])


def comp1(*args):
    first, rest = args[0], args[1:]
    if len(rest) == 0:
        return lambda *a, **k: first(*a, **k)
    elif len(rest) == 1:
        second = rest[0]
        return lambda *a, **k: first(second(*a, **k))
    else:
        return lambda *a, **k: comp1(first, comp1(*rest))(*a, **k)


## Example

# In [6]: comp(lambda x: x + 1, lambda x: x * 2, lambda x,y: x ** y)(10, 2)
# Out[6]: 201


## a more concise version using reduce that works for functions of
## arity 1 only. But may be it can be tweaked to work with multiple
## args? 

from functools import reduce, partial

def comp2(*args):
    return lambda a: partial(reduce, lambda x, y: y(x), reversed(args))(a)