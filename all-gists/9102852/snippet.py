import functools
import types


def gentramp(gen):
    def unroll(g):
        while isinstance(g, types.GeneratorType):
            g = g.next()
        return g

    @functools.wraps(gen)
    def decorated(*args, **kwargs):
        decorated.recur = gen
        return unroll(gen(*args, **kwargs))

    return decorated


@gentramp
def fact(n, acc=1):
    if n == 1:
        yield acc
    yield fact.recur(n - 1, n * acc)