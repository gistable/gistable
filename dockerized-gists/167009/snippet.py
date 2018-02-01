# Implementation of Simon Plouffe's formula for Pi in Hex
#
# James Tauber 2007-03-14
# http://jtauber.com/blog/2007/03/14/generating_the_hex_digits_of_pi/

def pi():
    N = 0
    n, d = 0, 1
    while True:
        xn = (120*N**2 + 151*N + 47)
        xd = (512*N**4 + 1024*N**3 + 712*N**2 + 194*N + 15)
        n = ((16 * n * xd) + (xn * d)) % (d * xd)
        d *= xd
        yield 16 * n // d
        N += 1