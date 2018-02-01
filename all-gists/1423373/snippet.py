import numpy as np
from scipy import linalg, optimize

MAX_ITER = 100


def group_lasso(X, y, alpha, groups, max_iter=MAX_ITER, rtol=1e-6,
             verbose=False):
    """
    Linear least-squares with l2/l1 regularization solver.

    Solves problem of the form:

               .5 * |Xb - y| + n_samples * alpha * Sum(w_j * |b_j|)

    where |.| is the l2-norm and b_j is the coefficients of b in the
    j-th group. This is commonly known as the `group lasso`.

    Parameters
    ----------
    X : array of shape (n_samples, n_features)
        Design Matrix.

    y : array of shape (n_samples,)

    alpha : float or array
        Amount of penalization to use.

    groups : array of shape (n_features,)
        Group label. For each column, it indicates
        its group apertenance.

    rtol : float
        Relative tolerance. ensures ||(x - x_) / x_|| < rtol,
        where x_ is the approximate solution and x is the
        true solution.

    Returns
    -------
    x : array
        vector of coefficients

    References
    ----------
    "Efficient Block-coordinate Descent Algorithms for the Group Lasso",
    Qin, Scheninberg, Goldfarb
    """

    # .. local variables ..
    X, y, groups, alpha = map(np.asanyarray, (X, y, groups, alpha))
    if len(groups) != X.shape[1]:
        raise ValueError("Incorrect shape for groups")
    w_new = np.zeros(X.shape[1], dtype=X.dtype)
    alpha = alpha * X.shape[0]

    # .. use integer indices for groups ..
    group_labels = [np.where(groups == i)[0] for i in np.unique(groups)]
    H_groups = [np.dot(X[:, g].T, X[:, g]) for g in group_labels]
    eig = map(linalg.eigh, H_groups)
    Xy = np.dot(X.T, y)
    initial_guess = np.zeros(len(group_labels))

    def f(x, qp2, eigvals, alpha):
        return 1 - np.sum( qp2 / ((x * eigvals + alpha) ** 2))
    def df(x, qp2, eigvals, penalty):
        # .. first derivative ..
        return np.sum((2 * qp2 * eigvals) / ((penalty + x * eigvals) ** 3))

    if X.shape[0] > X.shape[1]:
        H = np.dot(X.T, X)
    else:
        H = None

    for n_iter in range(max_iter):
        w_old = w_new.copy()
        for i, g in enumerate(group_labels):
            # .. shrinkage operator ..
            eigvals, eigvects = eig[i]
            w_i = w_new.copy()
            w_i[g] = 0.
            if H is not None:
                X_residual = np.dot(H[g], w_i) - Xy[g]
            else:
                X_residual = np.dot(X.T, np.dot(X[:, g], w_i)) - Xy[g]
            qp = np.dot(eigvects.T, X_residual)
            if len(g) < 2:
                # for single groups we know a closed form solution
                w_new[g] = - np.sign(X_residual) * max(abs(X_residual) - alpha, 0)
            else:
                if alpha < linalg.norm(X_residual, 2):
                    initial_guess[i] = optimize.newton(f, initial_guess[i], df, tol=.5,
                                args=(qp ** 2, eigvals, alpha))
                    w_new[g] = - initial_guess[i] * np.dot(eigvects /  (eigvals * initial_guess[i] + alpha), qp)
                else:
                    w_new[g] = 0.


        # .. dual gap ..
        max_inc = linalg.norm(w_old - w_new, np.inf)
        if True: #max_inc < rtol * np.amax(w_new):
            residual = np.dot(X, w_new) - y
            group_norm = alpha * np.sum([linalg.norm(w_new[g], 2)
                         for g in group_labels])
            if H is not None:
                norm_Anu = [linalg.norm(np.dot(H[g], w_new) - Xy[g]) \
                           for g in group_labels]
            else:
                norm_Anu = [linalg.norm(np.dot(H[g], residual)) \
                           for g in group_labels]
            if np.any(norm_Anu > alpha):
                nnu = residual * np.min(alpha / norm_Anu)
            else:
                nnu = residual
            primal_obj =  .5 * np.dot(residual, residual) + group_norm
            dual_obj   = -.5 * np.dot(nnu, nnu) - np.dot(nnu, y)
            dual_gap = primal_obj - dual_obj
            if verbose:
                print 'Relative error: %s' % (dual_gap / dual_obj)
            if np.abs(dual_gap / dual_obj) < rtol:
                break

    return w_new


def check_kkt(A, b, x, penalty, groups):
    """Check KKT conditions for the group lasso

    Returns True if conditions are satisfied, False otherwise
    """
    group_labels = [groups == i for i in np.unique(groups)]
    penalty = penalty * A.shape[0]
    z = np.dot(A.T, np.dot(A, x) - b)
    safety_net = 1e-1 # sort of tolerance
    for g in group_labels:
        if linalg.norm(x[g]) == 0:
            if not linalg.norm(z[g]) < penalty + safety_net:
                return False
        else:
            w = - penalty * x[g] / linalg.norm(x[g], 2)
            if not np.allclose(z[g], w, safety_net):
                return False
    return True


if __name__ == '__main__':
    from sklearn import datasets
    diabetes = datasets.load_diabetes()
    X = diabetes.data
    y = diabetes.target
    alpha = .1
    groups = np.r_[[0, 0], np.arange(X.shape[1] - 2)]
    coefs = group_lasso(X, y, alpha, groups, verbose=True)
    print 'KKT conditions verified:', check_kkt(X, y, coefs, alpha, groups)


