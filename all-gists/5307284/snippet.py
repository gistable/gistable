"""
The worst possible way to propagate uncertainties.
"""

import numpy as np
from scipy.stats import scoreatpercentile as sap

n = 1024
uplaces = 1 # the argument is that you generally only know your uncerts to 1 place
udtype = np.double

def _usable (q):
    if isinstance (q, Uval):
        return q.d
    return q

def _wrap (d):
    r = Uval (noinit=True)
    r.d = d
    return r

def _maybewrap (result, *inputs):
    for q in inputs:
        if isinstance (q, Uval):
            r = Uval (noinit=True)
            r.d = result
            return r
    return result


# Freestanding functions for which either argument can be anything
# numeric-friendly. Implementing (much of) the numpy standard functions.
# http://docs.scipy.org/doc/numpy/reference/routines.math.html

# No support for out= parameters right now. If implemented, it seems tricky
# to get the semantics right so add (1, 2).__class__ == int.

def sin (q):
    return _maybewrap (np.sin (_usable (q)), q)

def cos (q):
    return _maybewrap (np.cos (_usable (q)), q)

def tan (q):
    return _maybewrap (np.tan (_usable (q)), q)

# skipped: arcsin arccos arctan hypot arctan2 degrees radians
# unwrap deg2rad rad2deg sinh cosh tanh arcsinh arccosh arctanh
# around round_ rint fix floor ceil trunc

def exp (q):
    return _maybewrap (np.exp (_usable (q)), q)

def expm1 (q):
    return _maybewrap (np.expm1 (_usable (q)), q)

def exp2 (q):
    return _maybewrap (np.exp2 (_usable (q)), q)

def log (q):
    return _maybewrap (np.log (_usable (q)), q)

def log10 (q):
    return _maybewrap (np.log10 (_usable (q)), q)

def log2 (q):
    return _maybewrap (np.log2 (_usable (q)), q)

def log1p (q):
    return _maybewrap (np.log1p (_usable (q)), q)

# skipped: logaddexp logaddexp2 i0 sinc signbit copysign frexp
# ldexp

def add (left, right):
    return _maybewrap (_usable (left) + _usable (right), left, right)

def reciprocal (q):
    return _maybewrap (np.reciprocal (_usable (q)), q)

def negative (q):
    return _maybewrap (np.negative (_usable (q)), q)

def multiply (left, right):
    return _maybewrap (_usable (left) * _usable (right), left, right)

def divide (left, right):
    return _maybewrap (_usable (left) / _usable (right), left, right)

def power (left, right):
    return _maybewrap (_usable (left) ** _usable (right), left, right)

def subtract (left, right):
    return _maybewrap (_usable (left) - _usable (right), left, right)

def true_divide (left, right):
    return _maybewrap (np.true_divide (_usable (left), _usable (right)),
                       left, right)

def floor_divide (left, right):
    return _maybewrap (_usable (left) // _usable (right), left, right)

# skipped: fmod mod modf remainder angle real imag conj
# convolve clip

def sqrt (q):
    return _maybewrap (np.sqrt (_usable (q)), q)

def square (q):
    return _maybewrap (np.square (_usable (q)), q)

def absolute (q):
    return _maybewrap (np.absolute (_usable (q)), q)

def fabs (q):
    return _maybewrap (np.fabs (_usable (q)), q)

# skipped: sign maximum minimum

# Utilities that aren't standard math functions.

def bestval (q):
    if not isinstance (q, Uval):
        return q

    # http://www.roma1.infn.it/~dagos/asymmetric/node2.html says that the
    # "best" value is the barycenter of the distribution, i.e. the mean of our
    # samples (right?), not the median. TODO: investigate.

    return sap (q.d, 50.000)


def stdval (q):
    if not isinstance (q, Uval):
        return 0.0

    # TODO: figure out how to handle asymmetric error distributions! Should
    # pay attention to where this function is actually used to think about
    # the semantics that'd be the most helpful.

    return 0.5 * (sap (q.d, 84.134) - sap (q.d, 15.866))


def ufmt (q):
    if not isinstance (q, Uval):
        return '%g' % q

    # Same potential issue re: median-taking as mentioned above.

    lo = sap (q.d, 15.866)
    md = sap (q.d, 50.000)
    hi = sap (q.d, 84.134)

    if hi == lo:
        return '%g' % lo

    # Deltas. Round to limited # of places because we don't actually know the
    # fourth moment of the thing we're trying to describe.

    from numpy import abs, ceil, floor, log10

    dh = hi - md
    dl = md - lo

    p = int (ceil (log10 (dh)))
    rdh = round (dh * 10**(-p), uplaces) * 10**p
    p = int (ceil (log10 (dl)))
    rdl = round (dl * 10**(-p), uplaces) * 10**p

    # The least significant place to worry about is the L.S.P. of one of the
    # deltas, which is also its M.S.P. since we've just rounded them. Any
    # precision in the datum beyond this point is false.

    lsp = int (floor (log10 (min (rdh, rdl))))

    # We should round the datum since it might be something like 0.999+-0.1 and
    # we're about to try to decide what its most significant place is. Might get
    # -1 rather than 0.

    rmd = round (md, -lsp)

    if rmd == -0.: # 0 = -0, too, but no problem there.
        rmd = 0.

    # The most significant place to worry about is the M.S.P. of any of the
    # datum or the deltas. rdl and rdl must be positive, but not necessarily
    # rmd.

    msp = int (floor (log10 (max (abs (rmd), rdh, rdl))))

    # If we're not very large or very small, don't use scientific notation.

    if msp > -3 and msp < 3:
        srdh = '%.*f' % (-lsp, rdh)
        srdl = '%.*f' % (-lsp, rdl)

        if srdh == srdl:
            return '%.*fpm%s [%e %e %e]' % (-lsp, rmd, srdh, lo, md, hi)
        return '%.*fp%sm%s [%e %e %e]' % (-lsp, rmd, srdh, srdl, lo, md, hi)

    # Use scientific notation. Adjust values, then format.

    armd = rmd * 10**-msp
    ardh = rdh * 10**-msp
    ardl = rdl * 10**-msp
    prec = msp - lsp

    sardh = '%.*f' % (prec, ardh)
    sardl = '%.*f' % (prec, ardl)

    if sardh == sardl:
        return '(%.*fpm%s)e%d [%e %e %e]' % (prec, armd, sardh, msp, lo, md, hi)

    return '(%.*fp%sm%s)e%d [%e %e %e]' % (prec, armd, sardh, sardl, msp, lo, md, hi)


# A utility that we need for uneven error bounds. It does not appear to be
# possible to determine the needed parameters analytically.
#
# I spend a loooooong time trying to get identical logic to work with
# scipy.optimize. For some reason it never converged on sensible parameter
# values.

def findskewparams (mid, dhigh, dlow):
    from skewt import skewnorm
    from lsqmdl import Model

    assert dhigh > 0
    assert dlow < 0

    # we pass sqrt(scale) to the optimizer so that we can ensure the
    # positivity of scale itself in a simple way.

    def model (x, loc, rtsc, shape):
        return skewnorm.ppf (x, shape, loc=loc, scale=rtsc**2)

    x = [0.15866, 0.5, 0.84134]
    y = np.asarray ([mid + dlow, mid, mid + dhigh])
    guess = [mid, np.sqrt (0.5 * (dhigh - dlow)), 0.5 * (dhigh + dlow)]
    m = Model (model, x, y).solve (guess)
    return m.params[0], m.params[1]**2, m.params[2]


# The class.

def asuval (q):
    if isinstance (q, Uval):
        return q
    r = Uval (noinit=True)
    r.d = np.empty (n, dtype=udtype)
    r.d[:] = q
    return


def fromfixed (v):
    return Uval ().fromfixed (v)

def fromnorm (val, uncert):
    return Uval ().fromnorm (val, uncert)

def fromunif (lower_incl, upper_excl):
    return Uval ().fromunif (lower_incl, upper_excl)

def fromskew (val, dhigh, dlow):
    return Uval ().fromskew (val, dhigh, dlow)


class Uval (object):
    d = None

    def __init__ (self, noinit=False):
        if not noinit:
            # Precisely zero.
            self.d = np.zeros (n, dtype=udtype)

    def fromfixed (self, v):
        self.d.fill (v)
        return self

    def fromnorm (self, val, uncert):
        assert uncert >= 0
        self.d[:] = np.random.normal (val, uncert, n)
        return self

    def fromunif (self, lower_incl, upper_excl):
        assert upper_excl > lower_incl
        self.d[:] = np.random.uniform (lower_incl, upper_excl, n)
        return self

    def fromskew (self, val, dhigh, dlow):
        assert dhigh > 0
        assert dlow < 0
        from skewt import skewnorm

        loc, scale, shape = findskewparams (val, dhigh, dlow)
        self.d[:] = skewnorm.rvs (shape, loc=loc, scale=scale, size=n)
        return self

    # text

    def __str__ (self):
        return ufmt (self)

    def __repr__ (self):
        # XXX not quite appropriate -- temp hack
        return ufmt (self)

    # math -- http://docs.python.org/2/reference/datamodel.html#emulating-numeric-types

    def __add__ (self, other):
        return _wrap (self.d + _usable (other))

    def __sub__ (self, other):
        return _wrap (self.d - _usable (other))

    def __mul__ (self, other):
        return _wrap (self.d * _usable (other))

    def __floordiv__ (self, other):
        return _wrap (self.d // _usable (other))

    def __mod__ (self, other):
        return _wrap (self.d % _usable (other))

    def __divmod__ (self, other):
        return _wrap (divmod (self.d, _usable (other)))

    def __pow__ (self, other, modulo=None):
        if modulo is None:
            return _wrap (pow (self.d, _usable (other)))
        return _wrap (pow (self.d, _usable (other), _usable (modulo)))

    # skipped: lshift, rshift, and, xor, or

    def __div__ (self, other):
        return _wrap (self.d.__div__ (_usable (other)))

    def __truediv__ (self, other):
        return _wrap (self.d.__truediv__ (_usable (other)))

    def __radd__ (self, other):
        return _wrap (_usable (other) + self.d)

    def __rsub__ (self, other):
        return _wrap (_usable (other) - self.d)

    def __rmul__ (self, other):
        return _wrap (_usable (other) * self.d)

    def __rdiv__ (self, other):
        return _wrap (self.d.__rdiv__ (_usable (other)))

    def __rtruediv__ (self, other):
        return _wrap (_usable (other).__rtruediv__ (self.d))

    def __rfloordiv__ (self, other):
        return _wrap (_usable (other) // self.d)

    def __rmod__ (self, other):
        return _wrap (_usable (other) % self.d)

    def __rdivmod__ (self, other):
        return _wrap (divmod (_usable (other), self.d))

    def __rpow__ (self, other):
        return _wrap (_usable (other)**self.d)

    # skipped: rlshift, rrshift, rand, rxor, ror

    def __iadd__ (self, other):
        self.d += _usable (other)
        return self

    def __isub__ (self, other):
        self.d -= _usable (other)
        return self

    def __imul__ (self, other):
        self.d *= _usable (other)
        return self

    def __idiv__ (self, other):
        self.d *= _usable (other)
        return self

    def __itruediv__ (self, other):
        self.d.__itruediv__ (_usable (other))
        return self

    def __ifloordiv__ (self, other):
        self.d //= _usable (other)
        return self

    def __imod__ (self, other):
        self.d %= _usable (other)
        return self

    def __ipow__ (self, other, modulo=None):
        if modulo is None:
            self.d **= _usable (other)
        else:
            self.d.__ipow__ (_usable (other), _usable (modulo))
        return self

    # skipped: ilshift, irshift, iand, ixor, ior

    def __neg__ (self):
        self.d = -self.d
        return self

    def __pos__ (self):
        self.d = +self.d
        return self

    def __abs__ (self):
        self.d = np.abs (self.d)
        return self

    def __invert__ (self):
        self.d = ~self.d
        return self.d

    def __complex__ (self):
        # TODO: allow if we're actually a precise scalar, and suggest
        # a method that gives the median.
        raise TypeError ('uncertain value cannot be reduced to a complex scalar')

    def __int__ (self):
        raise TypeError ('uncertain value cannot be reduced to an integer scalar')

    def __long__ (self):
        raise TypeError ('uncertain value cannot be reduced to a long-integer scalar')

    def __float__ (self):
        raise TypeError ('uncertain value cannot be reduced to a float scalar')

    # skipped: oct, hex, index, coerce

    def __lt__ (self, other):
        raise TypeError ('uncertain value does not have a well-defined "<" comparison')

    def __le__ (self, other):
        raise TypeError ('uncertain value does not have a well-defined "<" comparison')

    def __eq__ (self, other):
        raise TypeError ('uncertain value does not have a well-defined "==" comparison')

    def __ne__ (self, other):
        raise TypeError ('uncertain value does not have a well-defined "!=" comparison')

    def __gt__ (self, other):
        raise TypeError ('uncertain value does not have a well-defined ">" comparison')

    def __ge__ (self, other):
        raise TypeError ('uncertain value does not have a well-defined ">=" comparison')

    def __cmp__ (self, other):
        raise TypeError ('uncertain value does not have a well-defined __cmp__ comparison')

    __hash__ = None

    def __nonzero__ (self):
        raise TypeError ('uncertain value does not have a well-defined boolean value')
