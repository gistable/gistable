from __future__ import division
import math
import sys

def gamma(n):
    return math.factorial(n - 1)

def h(a, b, c, d):
    num = gamma(a + c) * gamma(b + d) * gamma(a + b) * gamma(c + d)
    den = gamma(a) * gamma(b) * gamma(c) * gamma(d) * gamma(a + b + c + d)

    return num / den

def g0(a, b, c):
    return gamma(a + b) * gamma(a + c) / (gamma(a + b + c) * gamma(a))

def hiter(a, b, c, d):
    while d > 1:
        d -= 1
        yield h(a, b, c, d) / d

def g(a, b, c, d):
    return g0(a, b, c) + sum(hiter(a, b, c, d))

def print_odds(p):
    o = p / (1 - p)
    b = 10 * math.log(o, 10)

    if o > 1:
        s = "%.4f to 1" % o
    else:
        s = "1 to %.4f" % (1 / o)
    
    print s, "or %.4f dB" % b


def main():
    if len(sys.argv) != 5:
        sys.exit("Usage: %s succ1 fail1 succ2 fail2" % sys.argv[0])
    
    s1, f1, s2, f2 = map(int, sys.argv[1:])

    print_odds(g(s1 + 1, f1 + 1, s2 + 1, f2 + 1))

if __name__ == "__main__":
    main()