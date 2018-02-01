# -*- coding: utf-8 -*-
"""
Minimalistic implementation of l1 minimization via coordinate descent.

Reference: www.jstatsoft.org/v33/i01/paper

Author: Fabian Pedregosa <fabian@fseoane.net>
"""

import numpy as np

MAX_ITER = 100


def l1_coordinate_descent(X, y, alpha, max_iter=MAX_ITER):
    """
    Solves a problem of the form

        ||y - Xw||_2 ^2 + alpha ||w||_1

    by coordinate descent. This model is also known as the Lasso in machine learning.
    """

    beta = np.zeros(X.shape[1], dtype=X.dtype)
    alpha = alpha * X.shape[0]

    for _ in range(max_iter):
        for i in range(X.shape[1]):
            tmp = beta.copy()
            tmp[i] = 0.
            residual = np.dot(X[:, i], y - np.dot(X, tmp).T)
            beta[i] = np.sign(residual) * np.fmax(np.abs(residual) - alpha, 0) \
                / np.dot(X[:, i], X[:, i])
    return beta


def check_kkt_lasso(X, y, coef, penalty, tol=1e-3):
    """
    Check KKT conditions for Lasso
    """
    xr = np.dot(X.T, y - np.dot(X, coef))
    penalty = penalty * X.shape[0]
    nonzero = (coef != 0)
    return np.all(np.abs(xr[nonzero] - np.sign(coef[nonzero]) * penalty) < tol) \
        and np.all(np.abs(xr[~nonzero] / penalty) <= 1)


if __name__ == '__main__':
    # creates a random problem
    np.random.seed(0)
    X = np.random.randn(3, 3)
    y = np.random.randn(3)
    # estimates the lasso model
    coef = l1_coordinate_descent(X, y, .1)
    # checks the correctness of the solution by checking the KKT conditions
    print('KKT conditions satisfied: %s ' % check_kkt_lasso(X, y, coef, .1, .1))