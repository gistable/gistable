#!/usr/bin/env python
# encoding: utf8

# HAC 3.61: generates x_{i+1}, a_{i+1} and b_{i+1} 
# from a, b and c, partitioning the field
def step_xab(x, a, b, alpha, beta, n, Z):
    s = x % 3

    # S1
    if s == 1:
        x = x * beta % Z
        b = (b + 1) % n

    # S2
    if s == 0:
        x = pow(x, 2, Z)
        a = 2 * a % n
        b = 2 * b % n

    # S3
    if s == 2:
        x = x * alpha % Z
        a = (a + 1) % n

    return x, a, b

def naturals_from(n):
    while True:
        yield n
        n += 1

def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception("there's no inverse of %d on %d" %(a, m))
    else:
        return x % m

# Pollard's Rho algorithm for discrete logarithm (HAC 3.60).
# Returns the dlog of beta on the basis alpha and field Z
# n is the order of the field Z
def pollard_rho(alpha, beta, n, Z):
    x = {0: 1}
    a = {0: 0}
    b = {0: 0}

    # returns x, a, b for a given i using memoization
    def get_xab(i):
        if i not in x:
            _x, _a, _b = get_xab(i - 1)
            x[i], a[i], b[i] = step_xab(_x, _a, _b, alpha, beta, n, Z)
        return x[i], a[i], b[i]

    print "i\tx_i\ta_i\tb_i\tx_2i\ta_2i\tb_2i"
    for i in naturals_from(1):
        x_i, a_i, b_i = get_xab(i)
        x_2i, a_2i, b_2i = get_xab(2 * i)
        
        print "%d\t%d\t%d\t%d\t%d\t%d\t%d" % (i, x_i, a_i, b_i, x_2i, a_2i, b_2i)
        if x_i == x_2i:
            r = (b_i - b_2i) % n

            if r == 0:
                return False
            else:
                return modinv(r, n) * (a_2i - a_i) % n

# Example on HAC 3.61
alpha = 2
beta = 228
n = 191
Z = 383
l = pollard_rho(alpha, beta, n, Z)
if l:
    print "dlog(%d, %d, %d) = %d" % (alpha, beta, Z, l)