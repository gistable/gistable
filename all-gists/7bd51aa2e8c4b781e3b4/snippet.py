"""Transducers in Python

http://blog.cognitect.com/blog/2014/8/6/transducers-are-coming
"""

from functools import reduce


def compose(*fs):
    """Compose functions right to left.

    compose(f, g, h)(x) -> f(g(h(x)))

    Args:
        *fs: The rightmost function passed can accept any arguments and
            the returned function will have the same signature as
            this last provided function.  All preceding functions
            must be unary.

    Returns:
        The composition of the argument functions. The returned
        function will accept the same arguments as the rightmost
        passed in function.
    """
    if len(fs) < 1:
        raise TypeError("Cannot compose fewer than one functions")
    rfs = list(reversed(fs))

    def composed(*args, **kwargs):
        i = iter(rfs)
        f0 = next(i)
        result = f0(*args, **kwargs)
        for fn in i:
            result = fn(result)
        return result

    return composed


def identity(x):
    return x


# Example reducers

def append(result, item):
    """A reducer for appending to a list"""
    result.append(item)
    return result


# Functions for creating transducers, which are themselves
# functions which transform one reducer to another

def mapping(transform):
    """Create a mapping transducer with the given transform"""
    def transducer(reducer):
        def result_reducer(result, item):
            return reducer(result, transform(item))
        return result_reducer
    return transducer


def filtering(predicate):
    """Create a filtering transducer with the given predicate"""
    def transducer(reducer):
        def result_reducer(result, item):
            return reducer(result, item) if predicate(item) else result
        return result_reducer
    return transducer


def mapcatting(transform):
    """Create a transducer which transforms items and concatenates the results"""
    def transducer(reducer):
        """
        Args:
            reducer: The 'concatenation' reducer.
        """
        def result_reducer(result, item):
            return reduce(reducer, result, transform(item))
        return result_reducer
    return transducer


def taking(n):
    """Create a transducer which takes the first n items"""
    counter = 0

    def transducer(reducer):
        def result_reducer(result, item):
            nonlocal counter
            if counter < n:
                counter += 1
                return reducer(result, item)
            return result
        return result_reducer

    return transducer


def dropping_while(predicate):
    """Create a transducer which drops leading items while a predicate holds"""
    dropping = True

    def transducer(reducer):
        def result_reducer(result, item):
            nonlocal dropping
            dropping = dropping and predicate(item)
            return result if dropping else reducer(result, item)

        return result_reducer

    return transducer


def distinct():
    """Create a transducer which filters distinct items"""
    seen = set()

    def transducer(reducer):
        def result_reducer(result, item):
            if item not in seen:
                seen.add(item)
                return reducer(result, item)
            return result
        return result_reducer

    return transducer


def transduce(transducer, reducer, init, iterable):
    """A transducer helper for applying transducers to iterables"""
    # The standard library reduce function can be used for applying transducers to iterables
    return reduce(transducer(reducer), iterable, init)


r = transduce(transducer=compose(
                             mapping(lambda x: x*x),
                             filtering(lambda x: x % 5 != 0),
                             taking(6),
                             dropping_while(lambda x: x < 15),
                             distinct()),
              reducer=append,
              iterable=range(20),
              init=[])
print(r)
