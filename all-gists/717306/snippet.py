"""Prime number generation and number factorization."""

import bisect, itertools, random, sys

_primes = [2]

_miller_rabin_limit = 48611    # 5000th prime
_miller_rabin_security = 7

def modpow (a, b, c):
    """Efficiently compute (a^b)%c where a, b and c are positive integers."""
    if b == 1: return a % c
    d = b//2
    x = modpow (a, d, c)
    x = x*x%c
    if b % 2 == 1: x = x*a%c
    return x

def miller_rabin (n, t = _miller_rabin_security):
    """Apply Miller-Rabin primality test to detect whether n is prime or not.
    The test is run t times."""
    if n % 2 == 0: return False
    r = (n-1)//2
    for s in itertools.count (1):
        if r % 2: break
        r //= 2
    for tt in xrange (t):
        a = int (random.uniform (2, n-1))
        y = modpow (a, r, n)
        if y != 1 and y != n-1:
            for j in xrange (1, s):
                y = y**2 % n
                if y == 1: return False
                if y == n-1: break
            if y != n-1: return False
    return True

def _is_prime (i):
    if i > _miller_rabin_limit: return miller_rabin (i)
    s = int (i**0.5)
    for j in _primes:
        if i % j == 0: return False
        if j > s: return True
    return True

def _gen_primes ():
    for i in xrange (3, sys.maxint, 2):
        if _is_prime (i):
            _primes.append (i)
            yield i

_primary = _gen_primes ()

def _gen_primes (minval):
    i = 0
    if minval:
        l = _primes[-1]
        if minval > l:
            while minval > l: l =_primary.next ()
            i = len (_primes) - 1
        else:
            i = bisect.bisect_left (_primes, minval)
    for i in itertools.count (i):
        if i == len (_primes): yield _primary.next ()
        else: yield _primes[i]

def gen_primes (maxval = None, minval = None):
    """Prime numbers generator. If minval is given, only primes greater or
    equal to minval are returned. If maxval is given, only primes smaller
    or equal to maxval are returned.

    >>> for p in gen_primes(5): print p
    ...
    2
    3
    5
    7
    11"""
    if maxval:
        return itertools.takewhile (lambda x: x<=maxval, _gen_primes (minval))
    return _gen_primes (minval)

def gen_factors (n, duplicates = True):
    """Generator for factors of n (n > 1). If duplicates is False, do not
    send the same factor more than once."""
    assert n > 1
    if n > _miller_rabin_limit and miller_rabin (n):
        yield n
        return
    s = int (n**0.5)
    for i in gen_primes ():
        if i > s:
            yield n
            return
        if n % i == 0:
            yield i
            n //= i
            while n % i == 0:
                if duplicates: yield i
                n //= i
            if n == 1: return
            if n > _miller_rabin_limit and miller_rabin (n):
                yield n
                return
            s = int (n**0.5)

def factors (n):
    """Factorize n (n > 1) into its prime factors. Return a dictionary where
    keys are prime factors and values are powers.

    >>> factors(18)
    {2: 1, 3: 2}"""
    l = {}
    for i in gen_factors (n):
        try: l[i] += 1
        except KeyError: l[i] = 1
    return l

def factorslist (n):
    """Return a list of prime factors of n (n > 1).

    >>> factorslist(18)
    [2, 3, 3]"""
    return list (gen_factors (n))

def is_prime (n):
    """Check whether n is prime or not."""
    if n < 2: return False
    return gen_factors(n).next() == n

def ufactors (n):
    """Return the list of unique prime factors of n (n > 1).

    >>> ufactors(100)
    [2, 5]"""
    return list (gen_factors(n, duplicates = False))

def nfactors (n):
    """Return the number of unique prime factors of n."""
    return len (ufactors (n))

def totient (n):
    """Euler's totient function. Returns the number of integers between
    1 and n-1 relatively prime to n (n > 0).

    >>> totient(6)
    2
    (6 is relatively prime to 1 and 5)"""
    if n == 1: return 0
    num = den = 1
    for p in gen_factors (n, duplicates = False):
        num *= (p-1)
        den *= p
    return n * num // den

_s = {1: 1}
def s (n):
    """Sum of divisors of n (n > 0).

    >>> s(6)
    12
    (divisors of 6 are 1, 2, 3 and 6, summing to 12)"""
    if not _s.has_key (n):
        t = 1
        for (p, k) in factors(n).items():
            t *= (p**(k+1)-1)//(p-1)
        _s[n] = t
    return _s[n]

if __name__ == '__main__':
    # Quick test -- add primes up to 100,000 and compare to J result to:
    #   +/p:i.(p:^:_1)100000x
    assert sum (gen_primes (100000)) == 454396537
