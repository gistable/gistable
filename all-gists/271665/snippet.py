# A priority queue-based, wheel-using incremental Sieve of Eratosthenes.
# See `The Genuine Sieve of Eratosthenes' by Melissa E. O'Neill
# (http://www.cs.hmc.edu/~oneill/papers/Sieve-JFP.pdf)
# for the Haskell incremental sieve which inspired this implementation
# (along with detailed analyses of performance of several Haskell
# sieves).
#
# Usage:
#   Sieve()         -> simple SoE
#   Sieve(Wheel(4)) -> SoE + a wheel based on 4 initial primes
# Request primes through the iterator protocol.

import heapq
import itertools


def integers(start=0, stop=None, step=1):
    # well, this is the lil' bit of happy tomfoolery I just had to inject
    class Infinity(object):
        def __cmp__(self, i):
            return 1

    _stop = stop if stop is not None else Infinity()
    current = start
    while True:
        if _stop <= current:
            raise StopIteration
        yield current
        current += step

def divisible(n, k):
    return n % k == 0

def any(pred, vals):
    for v in vals:
        if pred(v):
            return True
    return False

def divisible_by_any(n, ks):
    return any(lambda k: divisible(n, k), ks)

def product(args):
    result = 1
    for arg in args:
        result *= arg
    return result


class CompositeEliminator(object):

    def __init__(self, prime):
        self.prime = prime
        self.composite = prime * prime

    def __cmp__(self, other):
        return cmp(self.composite, other.composite)

    def next(self):
        current = self.composite
        self.composite += self.prime
        return current


class Wheel(object):

    def __init__(self, n):
        tmp_sieve = Sieve()
        self.primes = [tmp_sieve.next() for i in xrange(n)]
        self.start = itertools.dropwhile(
                lambda n: divisible_by_any(n, self.primes),
                integers(max(self.primes)+1)
                ).next()
        not_skippable = list(itertools.ifilterfalse(
                    lambda k: divisible_by_any(k, self.primes),
                    integers(self.start, self.start + product(self.primes) + 1)
                ))
        self.increments = []
        i = 1
        while i < len(not_skippable):
            self.increments.append(not_skippable[i] - not_skippable[i-1])
            i += 1


class Sieve(object):

    def __init__(self, wheel=None):
        if wheel is not None:
            self._pq = [CompositeEliminator(p) for p in wheel.primes]
            heapq.heapify(self._pq)
            self._start = wheel.start
            self._increments = itertools.cycle(wheel.increments)
        else:
            self._pq = []
            heapq.heappush(self._pq, CompositeEliminator(2))
            self._start = 3
            self._increments = itertools.cycle([1])
        self._candidates = self._prepare_candidates()
        self._primes = self._prepare_primes()

    def __iter__(self):
        return self

    def next(self):
        return self._primes.next()

    def found_so_far(self):
        ps = map(lambda pq: pq.prime, self._pq)
        ps.sort()
        return ps

    def _prepare_candidates(self):
        current = self._start
        yield current
        while True:
            current += self._increments.next()
            yield current

    def _prepare_primes(self):
        for p in itertools.imap(lambda pq: pq.prime, self._pq):
            yield p

        for candidate in self._candidates:
            while True:
                eliminator = heapq.heappop(self._pq)
                if eliminator.composite == candidate:
                    eliminator.next()
                    heapq.heappush(self._pq, eliminator)
                    break
                elif eliminator.composite < candidate:
                    eliminator.next()
                    heapq.heappush(self._pq, eliminator)
                    continue
                else:
                    heapq.heappush(self._pq, eliminator)
                    heapq.heappush(self._pq, CompositeEliminator(candidate))
                    yield candidate
                    break