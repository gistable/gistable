# (C) Mathieu Blondel, November 2013
# License: BSD 3 clause

import numpy as np
from scipy.linalg import svd


def frequent_directions(A, ell, verbose=False):
    """
    Return the sketch of matrix A.

    Parameters
    ----------
    A : array-like, shape = [n_samples, n_features]
        Input matrix.

    ell : int
        Number of rows in the matrix sketch.

    Returns
    -------
    B : array-like, shape = [ell, n_features]

    Reference
    ---------
    Edo Liberty, "Simple and Deterministic Matrix Sketching", ACM SIGKDD, 2013.
    """
    if ell % 2 == 1:
        raise ValueError("ell must be an even number.")

    n_samples, n_features = A.shape

    if ell > n_samples:
        raise ValueError("ell must be less than n_samples.")

    if ell > n_features:
        raise ValueError("ell must be less than n_features.")

    B = np.zeros((ell, n_features), dtype=np.float64)
    ind = np.arange(ell)

    for i in xrange(n_samples):
        zero_rows = ind[np.sum(np.abs(B) <= 1e-12, axis=1) == n_features]
        if len(zero_rows) >= 1:
            B[zero_rows[0]] = A[i]
        else:
            U, sigma, V = svd(B, full_matrices=False)
            delta = sigma[ell / 2 - 1] ** 2
            sigma = np.sqrt(np.maximum(sigma ** 2 - delta, 0))
            B = np.dot(np.diag(sigma), V)

        if verbose:
            AA = np.dot(A.T, A)
            BB = np.dot(B.T, B)
            error = np.sum((AA - BB) ** 2)
            if i == 0:
                error_first = error
            print error / error_first

    return B

if __name__ == '__main__':
    np.random.seed(0)
    A = np.random.random((100, 20))

    B = frequent_directions(A, 10, verbose=True)
    print B.shape