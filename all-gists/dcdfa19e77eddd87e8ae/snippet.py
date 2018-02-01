import functools


def chain(*fs, reverse=True):
    def dec(g):
        @functools.wraps(g)
        def wrapper(*args, **kwargs):
            functions = reversed(fs) if reverse else fs
            a = lambda m, f: f(m)
            return functools.reduce(a, functions, g(*args, **kwargs))
        return wrapper
    return dec


# Exmaple
#
# def ts(t):
#     t2 = t * t
#     t3 = t2 * t
#     return [t3, t2, t, 1]
#
# tsrev = chain(list, reversed)(ts)
# OR
# @chain(list, reversed)
# def tsrev(t):
#     return ts(t)
