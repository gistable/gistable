from math import log
def primes_sieve(limit):
    a = [True] * limit                          # Initialize the primality list
    a[0] = a[1] = False

    for (i, isprime) in enumerate(a):
        if isprime:
            yield i
            for n in range(i*i, limit, i):     # Mark factors non-prime
                a[n] = False

primes = set(primes_sieve(10**7+1)) # sets have a fast membership check

def p_fac(n):
    if n in primes:
        return set([n])
    res = set()
    for p in primes:
        if n == 1:
            return res
        if n%p == 0:
            res.add(p)
            while n%p == 0:
                n /= p
    return res

def phi(n):
    if n in primes:
        return n - 1
    factors = p_fac(n)
    if len(factors) == 1:
        p, = factors
        a = int(log(n, p))
        return n - pow(p, a-1)
    res = n
    for f in factors:
        res *= (1-1.0/f)
    return int(res)

        
            