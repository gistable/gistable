# Python implementation of the Gibbons-Lester-Bird algorithm[1] for enumerating
# the positive rationals.
#
# James Tauber 2004-07-01
# http://jtauber.com/
#
# [1] http://web.comlab.ox.ac.uk/oucl/work/jeremy.gibbons/publications/rationals.pdf

def rationals():
    """
    generates the positive rationals with no duplicates.
    """
    r = (0,1)
    while True:
        r = (r[1], (r[1] * (r[0] // r[1])) + (r[1] - (r[0] % r[1])))
        yield r


# ANNOTATED VERSION
#
# def proper_fraction((n, d)):
#     return (n // d, (n % d, d))
#
# def reciprocal((n, d)):
#     return (d, n)
#
# def one_take((n, d)):
#     return (d - n, d)
#
# def improper_fraction(i, (n, d)):
#     return ((d * i) + n, d)
#
# def rationals():
#     r = (0,1)
#     while True:
#         n, y = proper_fraction(r)
#         z = improper_fraction(n, one_take(y))
#         r = reciprocal(z)
#         yield r