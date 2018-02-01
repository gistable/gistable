"""
NMF by coordinate descent, designed for sparse data (without missing values)
"""

# Author: Mathieu Blondel <mathieu@mblondel.org>
# License: BSD 3 clause

import numpy as np
import scipy.sparse as sp
import numba

from sklearn.base import BaseEstimator
from sklearn.utils import check_random_state
from sklearn.utils.extmath import safe_sparse_dot


@numba.jit("f8(f8[:,:], f8[:,:], f8[:,:], i4, f8, f8, f8)")
def _compute_update(H, PWW, PWV, penalty, alpha, regn, regd):
    violation = 0
    n_components = H.shape[0]

    for i in xrange(H.shape[1]):
        for k in xrange(n_components):

            if penalty == 2:
                regn = H[k, i] * alpha

            # gradient
            # g = GH[k, i] where GH = np.dot(PWW, H) - PWV
            g = - PWV[k, i] + regn

            for j in xrange(H.shape[0]):
                g += PWW[k, j] * H[j, i]

            # projected gradient
            pg = min(0, g) if H[k, i] == 0 else g

            # Hessian
            h = PWW[k, k] + regd

            # Update
            H[k, i] = max(H[k, i] - g / h, 0)

            violation += abs(pg)

    return violation


class CDNMF(BaseEstimator):
    """
    NMF by coordinate descent, designed for sparse data (without missing values)
    """

    def __init__(self, n_components=30, alpha=0.01, penalty="l2",
                 max_iter=50, tol=0.05,
                 init="random", random_state=None, verbose=0):
        self.n_components = n_components
        self.alpha = alpha
        self.penalty = penalty
        self.max_iter = max_iter
        self.tol = tol
        self.init = init
        self.random_state = random_state
        self.verbose = verbose

    def _init(self, X, rs, transpose=False):
        n_samples, n_features = X.shape

        if self.init == "random":
            W = rs.randn(self.n_components, n_features)
            np.abs(W, W)
        elif self.init == "sample":
            ind = np.arange(n_samples)
            rs.shuffle(ind)
            W = X[ind[:self.n_components]]
            if sp.issparse(W):
                W = W.toarray()
        comp = np.asfortranarray(W)

        # H is initialized empty since it will be optimized first.
        H = np.zeros((n_samples, self.n_components))
        coef = np.ascontiguousarray(H)

        if transpose:
            comp = comp.T
            coef = coef.T

        return comp, coef

    def _update(self, X, W, H, regn, regd, penalty):
        PWW = np.dot(W.T, W)
        PWV = safe_sparse_dot(W.T, X.T)

        return _compute_update(H, PWW, PWV, penalty,
                               self.alpha, regn, regd)

    def _fit_transform(self, X, W, H, update_W=True):
        penalties = {"l1": 1, "l2": 2}
        penalty = penalties[self.penalty]

        if penalty == 1:
            regn = self.alpha
            regd = 0
        else:
            regn = 0
            regd = self.alpha

        for t in xrange(self.max_iter):
            # Update H
            v = self._update(X, W, H, regn, regd, penalty)

            # Update W
            if update_W:
                v += self._update(X.T, H.T, W.T, regn, regd, penalty)

            if t == 0:
                violation_init = v

            if self.verbose:
                print "violation:", v / violation_init

            if v / violation_init <= self.tol:
                if self.verbose:
                    print "Converged at iteration", t + 1
                break

        return W, H

    def fit_transform(self, X):
        n_samples, n_features = X.shape
        rs = check_random_state(self.random_state)

        W, H = self._init(X, rs, transpose=True)

        W, H = self._fit_transform(X, W, H)

        self.components_ = W.T

        return H.T

    def fit(self, X):
        self.fit_transform(X)
        return self

    def transform(self, X):
        n_samples = X.shape[0]
        H = np.zeros((self.n_components, n_samples))
        W = self.components_.T
        W, H = self._fit_transform(X, W, H, update_W=False)
        return H.T


if __name__ == '__main__':
    from sklearn.datasets import fetch_20newsgroups_vectorized

    bunch = fetch_20newsgroups_vectorized(subset="all")
    X = bunch.data.tocsr()
    y = bunch.target

    nmf = CDNMF(init="sample", verbose=1, random_state=0)
    nmf.fit_transform(X)