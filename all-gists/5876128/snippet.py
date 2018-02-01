from fractions import gcd
from random import randrange

PRIMES_LE_31 = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31)
PRIMONIAL_31 = 200560490130


def invmul(x, mod):
    if mod <= 0:
        raise ValueError('Modulus must be greater than zero.')
    a = abs(x)
    b = mod
    c, d, e, f = 1, 0, 0, 1
    while b > 0:
        q, r = divmod(a, b)
        g = c - q * d
        h = e - q * f
        a, b, c, d, e, f = b, r, d, g, f, h
    if a != 1:
        raise ValueError('{x} has no multiplicative '
                         'inverse modulo {m}'.format(x=x, m=mod))
    return c * -1 if x < 0 else c * 1


def isqrt(n):
    if n < 0:
        raise ValueError('Square root is not defined for negative numbers.')
    x = int(n)
    if x == 0:
        return 0
    a, b = divmod(x.bit_length(), 2)
    n = 2 ** (a + b)
    while True:
        y = (n + x // n) >> 1
        if y >= n:
            return n
        n = y


def is_square(n):
    s = isqrt(n)
    return s * s == n


def factor(n, p=2):
    s = 0
    d = n - 1
    q = p

    while not d & q - 1:
        s += 1
        q *= p

    return s, d // (q // p)


def jacobi(a, p):
    if (not p & 1) or (p < 0):
        raise ValueError('p must be a positive odd number.')

    if (a == 0) or (a == 1):
        return a

    a = a % p
    t = 1

    while a != 0:
        while not a & 1:
            a >>= 1
            if p & 7 in (3, 5):
                t = -t

        a, p = p, a
        if (a & 3 == 3) and (p & 3) == 3:
            t = -t

        a = a % p

    if p == 1:
        return t

    return 0


def selfridge(n):
    d = 5
    s = 1
    ds = d * s

    while True:
        if gcd(ds, n) > 1:
            return ds, 0, 0

        if jacobi(ds, n) == -1:
            return ds, 1, (1 - ds) / 4

        d += 2
        s *= -1
        ds = d * s


def chain(n, u1, v1, u2, v2, d, q, m):
    k = q
    while m > 0:
        u2 = (u2 * v2) % n
        v2 = (v2 * v2 - 2 * q) % n
        q = (q * q) % n

        if m & 1 == 1:
            t1, t2 = u2 * v1, u1 * v2
            t3, t4 = v2 * v1, u2 * u1 * d
            u1, v1 = t1 + t2, t3 + t4

            if u1 & 1 == 1:
                u1 = u1 + n

            if v1 & 1 == 1:
                v1 = v1 + n

            u1, v1 = (u1 / 2) % n, (v1 / 2) % n
            k = (q * k) % n

        m = m >> 1

    return u1, v1, k


def strong_pseudoprime(n, a, s=None, d=None):
    if not n & 1:
        return False

    if (s is None) or (d is None):
        s, d = factor(n, 2)

    x = pow(a, d, n)

    if x == 1:
        return True

    for i in xrange(s):
        if x == n - 1:
            return True

        x = pow(x, 2, n)

    return False


def lucas_pseudoprime(n):
    if not n & 1:
        return False

    d, p, q = selfridge(n)
    if p == 0:
        return n == d

    u, v, k = chain(n, 0, 2, 1, p, d, q, (n + 1) >> 1)
    return u == 0


def strong_lucas_pseudoprime(n):
    if not n & 1:
        return False

    d, p, q = selfridge(n)
    if p == 0:
        return n == d

    s, t = factor(n + 2)

    u, v, k = chain(n, 1, p, 1, p, d, q, t >> 1)

    if (u == 0) or (v == 0):
        return True

    for i in xrange(1, s):
        v = (v * v - 2 * k) % n
        k = (k * k) % n
        if v == 0:
            return True

    return False


def miller_rabin(n, k=10):
    if n == 2:
        return True

    if not n & 1:
        return False

    if n < 2 or is_square(n):
        return False

    if gcd(n, PRIMONIAL_31) > 1:
        return n in PRIMES_LE_31

    s, d = factor(n)

    for i in xrange(k):
        a = randrange(2, n - 1)
        if not strong_pseudoprime(n, a, s, d):
            return False

    return True


def baillie_psw(n, limit=100):
    if n == 2:
        return True

    if not n & 1:
        return False

    if n < 2 or is_square(n):
        return False

    if gcd(n, PRIMONIAL_31) > 1:
        return n in PRIMES_LE_31

    bound = min(limit, isqrt(n))
    for i in xrange(3, bound, 2):
        if not n % i:
            return False

    return strong_pseudoprime(n, 2) \
        and strong_pseudoprime(n, 3) \
        and strong_lucas_pseudoprime(n)


def next_prime(n):
    if n < 2:
        return 2

    if n < 5:
        return [3, 5, 5][n - 2]

    gap = [1, 6, 5, 4, 3, 2, 1, 4, 3, 2, 1, 2, 1, 4, 3, 2, 1, 2, 1, 4, 3, 2, 1,
           6, 5, 4, 3, 2, 1, 2]

    n += 1 if not n & 1 else 2

    while not baillie_psw(n):
        n += gap[n % 30]

    return n
