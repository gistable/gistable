"""
(C) August 2013, Mathieu Blondel
# License: BSD 3 clause

This is a Numba-based reimplementation of the block coordinate descent solver
(without line search) described in the paper:

    Block Coordinate Descent Algorithms for Large-scale Sparse Multiclass
    Classification.  Mathieu Blondel, Kazuhiro Seki, and Kuniaki Uehara.
    Machine Learning, May 2013.

The reference Cython implementation is avaible from the "primal_cd" module in:
    https://github.com/mblondel/lightning

The reference Cython implementation appears to be roughly 2x faster than this
implementation.
"""

from numba import jit

import numpy as np
import scipy.sparse as sp

from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.extmath import safe_sparse_dot


@jit("void(f8[:], i4[:], f8, f8[:])")
def _inv_step_sizes(X_data, X_indptr, scale, out):
    """Compute the block-wise inverse step sizes (Lipschitz constants)."""
    n_features = out.shape[0]

    for j in xrange(n_features):
        sqnorm = 0
        for k in xrange(X_indptr[j], X_indptr[j+1]):
            sqnorm += X_data[k] * X_data[k]
        out[j] = scale * sqnorm


@jit("void(f8[:], i4[:], i4[:], i4[:], f8[:,:], i4, f8, f8[:])")
def _grad(X_data, X_indices, X_indptr, y, A, j, C, out):
    """Compute the partial gradient for the j^th block
       (vector of size n_classes)."""
    n_classes = out.shape[0]

    for r in xrange(n_classes):
        for k in xrange(X_indptr[j], X_indptr[j+1]):
            i = X_indices[k]

            if y[i] == r:
                continue

            if A[r, i] > 0:
                out[y[i]] -= 2 * C * A[r, i] * X_data[k]
                out[r] += 2 * C * A[r, i] * X_data[k]


@jit("void(f8[:], i4, f8, f8, f8[:], f8[:, :])")
def _update_coef(grad, j, step_size, alpha, update, coef):
    """Update the j^th block of the coefficient matrix."""
    n_classes = grad.shape[0]

    update_norm = 0

    for r in xrange(n_classes):
        update[r] = coef[r, j] - step_size * grad[r]
        update_norm += update[r] * update[r]

    update_norm = np.sqrt(update_norm)

    mu = alpha * step_size
    scale = 1 - mu / update_norm
    if scale < 0:
        scale = 0

    for r in xrange(n_classes):
        old = coef[r, j]
        coef[r, j] = scale * update[r]
        update[r] = coef[r, j] - old


@jit("void(f8[:], i4[:], i4[:], i4[:], i4, f8[:], f8[:, :])")
def _update_A(X_data, X_indices, X_indptr, y, j, update, A):
    """Update matrix A (see paper)."""
    n_classes = A.shape[0]

    for r in xrange(n_classes):
        for k in xrange(X_indptr[j], X_indptr[j+1]):
            i = X_indices[k]

            if y[i] == r:
                continue

            A[r, i] += (update[r] - update[y[i]]) * X_data[k]


@jit("f8(f8[:], f8[:], i4, f8)")
def _violation(grad, coef, j, alpha):
    """Compute optimality violation for the j^th block."""
    n_classes = grad.shape[0]

    coef_norm = 0
    grad_norm = 0

    for r in xrange(n_classes):
        coef_norm += coef[r, j] * coef[r, j]
        grad_norm += grad[r] * grad[r]

    grad_norm = np.sqrt(grad_norm)

    if coef_norm == 0:
        violation = max(grad_norm - alpha, 0)
    else:
        violation = np.abs(grad_norm - alpha)

    return violation


@jit("void(f8[:], i4[:], i4[:], i4[:], i4, f8, f8, f8, i4, f8[:,:])")
def _fit(X_data, X_indices, X_indptr, y, max_iter, alpha, C, tol,
         verbose, coef):
    n_samples = y.shape[0]
    n_classes, n_features = coef.shape
    inv_step_sizes = np.zeros(n_features, dtype=np.float64)
    _inv_step_sizes(X_data, X_indptr, C * 4 * (n_classes-1), inv_step_sizes)

    grad = np.zeros(n_classes, dtype=np.float64)
    update = np.zeros(n_classes, dtype=np.float64)
    A = np.ones((n_classes, n_samples), dtype=np.float64)

    rs = np.random.RandomState(None)

    violation_init = 0
    for it in xrange(max_iter):
        violation_max = 0

        for _ in xrange(n_features):
            j = rs.randint(n_features-1)

            if inv_step_sizes[j] == 0:
                continue

            grad.fill(0)
            _grad(X_data, X_indices, X_indptr, y, A, j, C, grad)
            violation = _violation(grad, coef, j, alpha)
            _update_coef(grad, j, 1. / inv_step_sizes[j], alpha, update, coef)
            _update_A(X_data, X_indices, X_indptr, y, j, update, A)

            if violation > violation_max:
                violation_max = violation

        if it == 0:
            violation_init = violation_max

        if verbose >= 1:
            print violation_max / violation_init

        if violation_max / violation_init < tol:
            if verbose >= 1:
                print "Converged at iter", it + 1
            break


class SparseMulticlassClassifier(BaseEstimator, ClassifierMixin):

    def __init__(self, alpha=1, C=1, max_iter=20, tol=0.05, verbose=0):
        self.alpha = alpha
        self.C = C
        self.max_iter = max_iter
        self.tol = tol
        self.verbose = verbose


    def fit(self, X, y):
        X = sp.csc_matrix(X)

        n_samples, n_features = X.shape

        self._enc = LabelEncoder()
        y = self._enc.fit_transform(y).astype(np.int32)
        n_classes = len(self._enc.classes_)

        self.coef_ = np.zeros((n_classes, n_features), dtype=np.float64)

        _fit(X.data, X.indices, X.indptr, y, self.max_iter,
             self.alpha, self.C, self.tol, self.verbose, self.coef_)

        return self

    def decision_function(self, X):
        return safe_sparse_dot(X, self.coef_.T)

    def predict(self, X):
        pred = self.decision_function(X)
        pred = np.argmax(pred, axis=1)
        return self._enc.inverse_transform(pred)

    def n_nonzero(self, percentage=False):
        n_nz = np.sum(np.sum(self.coef_ != 0, axis=0, dtype=bool))

        if percentage:
            n_nz /= float(self.coef_.shape[1])

        return n_nz


if __name__ == '__main__':
    import time

    from sklearn.datasets import fetch_20newsgroups_vectorized

    bunch = fetch_20newsgroups_vectorized(subset="all")
    X = bunch.data
    y = bunch.target

    print X.shape

    s = time.time()
    clf = SparseMulticlassClassifier(C=1./X.shape[0], alpha=1e-4, tol=1e-3,
                                     max_iter=20, verbose=0)
    clf.fit(X, y)
    training_time = time.time() - s

    print "Numba"
    print training_time
    print clf.score(X, y)
    print clf.n_nonzero(percentage=True)
    print

    from lightning.primal_cd import CDClassifier
    clf = CDClassifier(C=1./X.shape[0], alpha=1e-4, tol=1e-3, max_iter=20,
                       multiclass=True, penalty="l1/l2", shrinking=False,
                       max_steps=0, selection="uniform", verbose=0)
    s = time.time()
    clf.fit(X, y)
    training_time = time.time() - s

    print "Cython"
    print training_time
    print clf.score(X, y)
    print clf.n_nonzero(percentage=True)
    print
