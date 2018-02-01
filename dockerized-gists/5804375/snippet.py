from collections import deque
from functools import wraps


def inversify(predicate):
    """Returns a predicate that is the inverses of the given predicate."""
    @wraps(predicate)
    def _inner(*args, **kwargs):
        return not predicate(*args, **kwargs)
    return _inner


class Sieve(object):
    """Helper class for the sift() function."""
    def __init__(self, iterable, key):
        self.buffer = deque()
        self.iterable = iterable
        self.key = key
        self.inverse = None

    def push(self, item):
        self.buffer.append(item)

    def __iter__(self):
        return self

    def next(self):
        if self.buffer:
            return self.buffer.popleft()
        else:
            while True:
                item = self.iterable.next()
                if self.key(item):
                    return item
                else:
                    self.inverse.push(item)


def sift(iterable, key):
    """Sifts an iterable, returning two iterables: matches and non-matches.
    Consumes the whole iterable.

    >>> even, odd = sift(xrange(10), key=lambda x: x % 2 == 0)
    >>> list(even)
    [0, 2, 4, 6, 8]
    >>> list(odd)
    [1, 3, 5, 7, 9]
    """
    it = iter(iterable)
    even = Sieve(it, key)
    odd = Sieve(it, inversify(key))
    even.inverse, odd.inverse = odd, even
    return even, odd
