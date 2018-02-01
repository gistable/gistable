""" Poisson-loss Factorization Machines with Numba

Follows the vanilla FM model from:
Steffen Rendle (2012): Factorization Machines with libFM.
In: ACM Trans. Intell. Syst. Technol., 3(3), May.
http://doi.acm.org/10.1145/2168752.2168771

See also: https://github.com/coreylynch/pyFM
"""

# Author: Vlad Niculae <vlad@vene.ro>
# License: Simplified BSD

from __future__ import print_function
import numpy as np
from numba import jit
from scipy import sparse as sp

from sklearn.utils import check_random_state, check_array, check_X_y
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import OneHotEncoder


@jit("f8(f8[:], i4[:], f8[:], f8[:], f8[:,:], f8[:])", nopython=True)
def _fm_predict(row_data, row_indices, scaling, w, V, Vx):
    """Factorization machine forward pass"""
    pred = 0
    for i in range(row_indices.shape[0]):
        pred += w[row_indices[i]] * row_data[i]
    pred *= scaling[1]  # pred = wscale * dot(x, w/wscale)

    pred += scaling[0]  # add bias

    second_order = 0
    for d in range(V.shape[1]):
        Vx[d] = 0
        for i in range(row_indices.shape[0]):
            v_id = V[row_indices[i], d]
            Vx[d] += v_id * row_data[i]
            second_order -= (v_id ** 2) * (row_data[i] ** 2)
        second_order += Vx[d] ** 2
        Vx[d] *= scaling[2]  # Vx = Vscale * dot(V/Vscale, x),
    second_order *= 0.5 * scaling[2] ** 2
    # second_order = 1/2 Vscale^2 * [dot(V/Vscale, x)^2 - (V/Vscale)^2 * x^2]
    pred += second_order
    return pred


@jit("f8[:](f8[:], i4[:], i4[:], f8[:], f8[:], f8[:,:], i4)")
def _fm_predict_batch_fast(X_data, X_indices, X_indptr, scaling, w, V,
                           n_samples):
    res = np.zeros(n_samples, dtype=np.double)
    for i in range(n_samples):
        for k in range(X_indptr[i], X_indptr[i + 1]):
            res[i] += w[X_indices[k]] * X_data[k]
        res[i] *= scaling[1]
        res[i] += scaling[0]
        second_order = 0
        for d in range(V.shape[1]):
            vx = 0
            for k in range(X_indptr[i], X_indptr[i + 1]):
                v_id = V[X_indices[k], d]
                vx += v_id * X_data[k]
                second_order -= (v_id ** 2) * (X_data[i] ** 2)
            second_order += vx ** 2
        second_order *= 0.5 * scaling[2] ** 2
        res[i] += second_order
    return res


def _fm_predict_batch(X, scaling, w, V):
    """Factorization machine prediction over a batch."""
    return _fm_predict_batch_fast(X.data, X.indices, X.indptr, scaling, w, V,
                                  X.shape[0])


@jit('void(f8[:], i4[:], f8, f8[:], f8[:], f8[:, :], f8, f8, f8)',
     nopython=True)
def _fm_poisson_step(data, indices, y, scaling, w, V, learning_rate, reg_w,
                     reg_V):
    Vx = np.empty(V.shape[1], dtype=np.double)  # byproduct of _fm_predict
    z = _fm_predict(data, indices, scaling, w, V, Vx)
    # loss: exp(z) - y * z + y! (y! = ln gamma(y + 1))
    dloss_dz = np.exp(z) - y

    # update bias:
    scaling[0] -= learning_rate * dloss_dz

    # update w: gradw_i = x_i
    for k in range(indices.shape[0]):
        w[indices[k]] -= learning_rate * dloss_dz * data[k] / scaling[1]

    # update V:  d indexes latent dims, i=indices[k] indexes nonzero features
    # gradv_id = x_i * sum(v_jd x_j) - v_id * x_i^2
    for d in range(V.shape[1]):
        for k in range(indices.shape[0]):
            grad_v = data[k] * Vx[d] / scaling[2]
            grad_v -= V[indices[k], d] * data[k] ** 2
            V[indices[k], d] -= learning_rate * dloss_dz * grad_v

    # L2-regularize without touching the data
    # Inspired by the scikit-learn stochastic gradient descent approach
    # do not scale to negative values reg_* is too big: instead set to zero
    scaling[1] *= max(0, 1.0 - learning_rate * reg_w)
    scaling[2] *= max(0, 1.0 - learning_rate * reg_V)


@jit("void(f8[:], i4[:], i4[:], f8[:], f8[:], f8[:], f8[:, :], f8, f8, f8)",
     nopython=True)
def _fm_poisson_epoch(X_data, X_indices, X_indptr, y, scaling, w, V,
                      learning_rate, reg_w, reg_V):
    n_samples = y.shape[0]
    for i in range(n_samples):
        _fm_poisson_step(X_data[X_indptr[i]:X_indptr[i + 1]],
                         X_indices[X_indptr[i]:X_indptr[i + 1]],
                         y[i], scaling, w, V, learning_rate, reg_w, reg_V)


def factorization_machine_poisson(X, y, X_val=None, y_val=None, n_latent=3,
                                  reg_w=1., reg_V=1., init_std=0.001,
                                  warm_start=None, learning_rate=0.01,
                                  n_iter=10, verbose=False, random_state=None):
    """Learns a factorization machine model with Poisson loss by SGD.

    The response is modeled as:
        y = exp(intercept + <w, x> + sum_i sum_j>i <x_i * v_i, x_j * v_j>,

    where <., .> is the dot product,
    w is a vector of length n_features capturing first-degree effects
    and V is an array (n_features, n_latent) for second-degree interactions.

    The Poisson loss is appropriate for count and rate outputs.

    Parameters
    ----------
    X: array-like or sparse, shape: (n_samples, n_features)
        Training data points.

    y: array, shape: (n_samples,)
        Target labels.

    X_val: array-like or sparse, shape: (n_samples_val, n_features), optional
        Validation data points. Used only if verbose != False

    y_val: array, shape: (n_samples_val,), optional
        Validation labels. Used only if verbose != False

    n_latent: int,
        Latent dimensions of the second-degree model. Default: 3

    reg_w: float,
        Regularization amount for first-degree weights. Default: 1

    reg_V: float,
        Regularization amount for second-degree weights. Default: 1

    init_std: float,
        Initial scale of weight values. (Used only if warm_start is None.)
        Weights are initialized from a centered gaussian with init_std scale.
        Default: 0.001

    warm_start: tuple (intercept, w, V) or None,
        Initial setting for the weights.

    learning_rate: float,
        Step size for stochastic gradient descent. Default: 0.01

    n_iter: int,
        Maximum number of passes over the training data. Default: 10

    verbose: int,
        If > 0, prints statistics at every `verbose` iteration. Default: False.

    random_state: int, RandomState or None:
        Seed for the random number generator.

    Returns
    -------

    scaling: tuple (intercept, w_scale, V_scale),
        Scales of the learning parameters.

    w: array, shape (n_features,):
        First degree coefficients, divided by w_scale (see scaling above)

    V: array, shape (n_features, n_latent):
        Embedded second-degree interaction weights, divided by V_scale.

    """
    X, y = check_X_y(X, y, accept_sparse='csr', dtype=np.double)
    y = y.astype(np.double)
    if not sp.issparse(X):  # force sparse
        X = sp.csr_matrix(X)
    if X_val is not None:
        X_val, y_val = check_X_y(X_val, y_val, accept_sparse='csr',
                                 dtype=np.double)
        if not sp.issparse(X):
            X = sp.csr_matrix(X)

    n_samples, n_features = X.shape
    rng = check_random_state(random_state)

    reg_w *= 0.5
    reg_V *= 0.5 * n_latent  # Unsure about the correct scaling

    # initialize
    if warm_start is not None:
        bias, w, V = warm_start
        scaling = np.array([bias, 1, 1], dtype=np.double)
    else:
        w = rng.randn(n_features)
        V = rng.randn(n_features, n_latent)
        scaling = np.array([0, init_std, init_std], dtype=np.double)

    for it in range(n_iter):
        if verbose and it % verbose == 0:
            pred_tr = _fm_predict_batch(X, scaling, w, V)
            pred_te = _fm_predict_batch(X_val, scaling, w, V)
            np.exp(pred_tr, out=pred_tr)
            np.exp(pred_te, out=pred_te)
            dloss = np.mean(y - pred_tr)
            print(
                "{:>3}: dloss={:<8.4f} MSE tr={:<4.2f}, valid={:4.2f}".format(
                    it,
                    dloss,
                    mean_squared_error(y, pred_tr),
                    mean_squared_error(y_val, pred_te)),
                end=" ")

        _fm_poisson_epoch(X.data, X.indices, X.indptr, y, scaling, w, V,
                          learning_rate, reg_w, reg_V)

        # rescale if needed
        if scaling[1] <= 1e-9:
            w *= scaling[1]
            scaling[1] = 1.0

        if scaling[2] <= 1e-9:
            V *= scaling[2]
            scaling[2] = 1.0

        if verbose and it % verbose == 0:
            print("w_0={:<6.2f} ||w||={:<6.2f} ||V||={:<6.2f}".format(
                scaling[0],
                np.linalg.norm(w * scaling[1]),
                np.linalg.norm(V.ravel() * scaling[2])))
    return scaling, w, V


def array_to_fm_format(X):
    """Converts a dense or sparse array X to factorization machine format.

    If x[i, j] is represented (if X is sparse) or not nan (if dense)
    the output will have a row:
        [one_hot(i), one_hot(j)] -> x[i, j]

    Parameters
    ----------
    X, array-like or sparse
        Input array

    Returns
    -------
    X_one_hot, sparse array, shape (n_x_entries, X.shape[1] + X.shape[2])
        Indices of non-empty values in X, in factorization machine format.

    y: array, shape (n_x_entries,)
        Non-empty values in X.
    """
    X = check_array(X, accept_sparse='coo', force_all_finite=False)
    n_rows, n_cols = X.shape
    encoder = OneHotEncoder(n_values=[n_rows, n_cols])
    if sp.issparse(X):
        y = X.data
        X_ix = np.column_stack([X.row, X.col])
    else:
        ix = np.isfinite(X)
        X_ix = np.column_stack(np.where(ix))
        y = X[ix].ravel()
    X_oh = encoder.fit_transform(X_ix)
    return X_oh, y


if __name__ == '__main__':
    from scipy.stats.distributions import poisson
    from sklearn.cross_validation import train_test_split
    from time import time

    X_dense = poisson.rvs(mu=3, size=(500, 600), random_state=0)
    X, y = array_to_fm_format(X_dense)
    X, X_val, y, y_val = train_test_split(X, y, random_state=0)
    for reg in (0, 1e-5):
        print("Regularization: {}".format(reg))
        t0 = time()
        w_0, w, V = factorization_machine_poisson(
            X, y, X_val, y_val, n_latent=50,
            reg_w=reg, reg_V=reg,
            init_std=0.01, learning_rate=5e-3, n_iter=31, verbose=10,
            random_state=0)
        print("Done in {}".format(time() - t0))
