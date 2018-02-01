#!/usr/bin/env python
"""Solution for project euler problem #12.

Based on:
http://stackoverflow.com/questions/571488/project-euler-12-in-python/571526#571526
"""

def ndiv(n, prime_factors):
    """Return number of divisors of `n`.

    prime_factors: prime factors of `n`.

    >>> from itertools import starmap
    >>> list(starmap(ndiv, ((1, []), (12, [2, 3]))))
    [1, 6]
    """
    assert n > 0
    phi = 1
    for prime in prime_factors: 
        alpha = 0 # multiplicity of `prime` in `n`
        q, r = divmod(n, prime)
        while r == 0: # `prime` is a factor of `n`
            n = q
            alpha += 1
            q, r = divmod(n, prime)
        phi *= alpha + 1 # see http://en.wikipedia.org/wiki/Divisor_function
    return phi         

def prime_factors_gen():
    """Yield prime factors for each natural number.
    
    Based on 
    http://stackoverflow.com/questions/567222/simple-prime-generator-in-python/568618#568618

    >>> from itertools import islice
    >>> list(islice(prime_factors_gen(), 20)) #doctest:+NORMALIZE_WHITESPACE
    [(1, []), (2, [2]), (3, [3]), (4, [2]), (5, [5]), (6, [3, 2]),
    (7, [7]), (8, [2]), (9, [3]), (10, [5, 2]), (11, [11]), (12, [3, 2]),
    (13, [13]), (14, [7, 2]), (15, [5, 3]), (16, [2]), (17, [17]),
    (18, [3, 2]), (19, [19]), (20, [5, 2])]
    """
    D = {1:[]} # nonprime -> prime factors of `nonprime`
    #NOTE: dictionary could be replaced by priority queue
    q = 1
    while True: # Sieve of Eratosthenes algorithm
        if q not in D: # `q` is a prime number
            D[q + q] = [q]
            yield q, [q] 
        else: # q is a composite
            for p in D[q]: # `p` is a factor of `q`
                # therefore `p` is a factor of `p + q` too
                D.setdefault(p + q, []).append(p)
            yield q, D[q]
            del D[q]
        q += 1

def highly_composite_triangular(max_ndivisors):
    """
    Return the smallest triangular number that has more than
    max_ndivisors divisors.

    >>> # the first 25 highly compisite triangular numbers
    >>> hcts = (1, 3, 6, 28, 36, 120, 300, 528, 630, 2016,
    ...         3240, 5460, 25200, 73920, 157080, 437580,
    ...         749700, 1385280, 1493856, 2031120, 2162160,
    ...         17907120, 76576500, 103672800, 236215980)
    ...
    >>> # corresponding hct has >= number of divisors
    >>> ndivs = (1, 2, 3, 5, 7, 10, 17, 19, 21, 25, 37, 41,
    ...          49, 91, 113, 129, 145, 163, 169, 193, 241,
    ...          321, 481, 577, 649)
    >>> for maxndiv, t in zip(ndivs, hcts):
    ...     h = highly_composite_triangular(maxndiv - 1)
    ...     if h != t:
    ...        print maxndiv, h, t
    ...        break
    ... else:
    ...     print "ok"
    ...
    ok
    """
    ndivs = {0: 0} # n -> number of divisors
    for n, pfs in prime_factors_gen():
        # save number of divisor of `n`
        ndivs[n] = ndiv(n, pfs)
        # decompose `(n-1)`th triangular number: `n * (n - 1) // 2`
        half, odd = (n//2, n-1) if n % 2 == 0 else ((n - 1)//2, n)
        # n and (n-1) do not have common factors, therefore
        # ndiv(n * (n - 1)) == ndiv(n) * ndiv(n-1)
        #NOTE: we already cached ndiv therefore there is no need to
        #      to save ndivs[half], ndivs[odd] for further use
        if ndivs[half] * ndivs[odd] > max_ndivisors:
            return half * odd  # `(n-1)`th triangular number

def main():
    import time
    start = time.clock()
    h = highly_composite_triangular(500)
    print "%d (%.2g seconds)" % (h, time.clock() - start)

if __name__=="__main__":
    main()
    import doctest; doctest.testmod()
