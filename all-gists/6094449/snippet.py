# Author: Denis A. Engemann <d.engemann@fz-juelich.de>
#
# License: BSD (3-clause)

""" Profile fast_dot versus np.dot

Dependencies
------------
scikit-learn
https://github.com/fabianp/memory_profiler

Usage
-----

mprof run --python run_profile_fast_dot.py
mprof plot

"""
import numpy as np
from sklearn.utils.validation import array2d
from scipy import linalg


def _impose_f_order(X):
    """Helper Function"""
    # important to access flags instead of calling np.isfortran,
    # this catches corner cases.
    if X.flags.c_contiguous:
        return array2d(X.T, copy=False, order='F'), True
    else:
        return array2d(X, copy=False, order='F'), False


def fast_dot(A, B):
    """Compute fast dot products directly calling BLAS.

    This function calls BLAS directly while warranting Fortran contiguity.
    This helps avoiding extra copies `np.dot` would have created.
    For details see section `Linear Algebra on large Arrays`:
    http://wiki.scipy.org/PerformanceTips

    Parameters
    ----------
    A, B: instance of np.ndarray
        input matrices.
    """
    if A.dtype != B.dtype:
        raise ValueError('A and B must be of the same type.')
    if A.dtype not in (np.float32, np.float64):
        raise ValueError('Data must be single or double precision float.')

    dot = linalg.get_blas_funcs('gemm', (A, B))
    A, trans_a = _impose_f_order(A)
    B, trans_b = _impose_f_order(B)
    return dot(alpha=1.0, a=A, b=B, trans_a=trans_a, trans_b=trans_b)


n_samples = 1e6 / 2
n_features = 250
rng = np.random.RandomState(42)
W = rng.random_sample([n_features, n_features])
X = rng.random_sample([n_samples, n_features])

print 'estimated data size in memory'
print '%i MB' % (X.size * X.itemsize / 1e6)
print '%s' % X.dtype

with profile.timestamp('naive-dot-rect'):
    np.dot(W, X.T)

with profile.timestamp('fast-dot-rect'):
    fast_dot(W, X.T)


with profile.timestamp('naive-dot-square'):
    np.dot(W, W.T)

with profile.timestamp('fast-dot-square'):
    fast_dot(W, W.T)
