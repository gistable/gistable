import numpy as np
from numpy.linalg import norm, solve
from scipy.spatial.distance import cdist
from sklearn.neighbors import kneighbors_graph


def phi(l, mu):
    return (mu * (np.sqrt(l) - 1)**2)


def eye_vector(length, position):
    v = np.zeros((length, ))
    v[position] = 1
    return v


def computeA(W, L):
    n = W.shape[0]
    A = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            e = eye_vector(n, i) - eye_vector(n, j)
            A += W[i, j] * L[i, j] * np.dot(np.atleast_2d(e).T, np.atleast_2d(e))
    return A


def l2norm(x):
    return np.sqrt(np.sum(x**2))


def objective(X, U, W, L, landa, mu):
    n = X.shape[0]

    # First term
    diff = X - U
    f = 0.5 * np.sum([l2norm(x)**2 for x in diff])

    # Second term
    s = 0.0
    for i in range(n):
        for j in range(n):
            s += W[i, j] * (L[i, j] * l2norm(U[i] - U[j])**2 + phi(L[i, j], mu))
    s *= landa/2
    return f + s


def update_L(U, mu):
    n = U.shape[0]
    L = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            L[i, j] = (mu / (mu + l2norm(U[i] - U[j])**2))
    return L


def RobustContinuousClustering(X, W, offset_mu=100, delta=0.05, eps=1e-4,
                               max_iter=100):
    n_samples = X.shape[0]
    d = X.shape[1]
    chi = norm(X, ord=2)

    U = X.copy()

    L = np.ones((n_samples, n_samples))
    dists = cdist(X, X, metric='euclidean')
    lower_bound_mu = np.max(dists**2)
    mu = offset_mu + lower_bound_mu
    A = computeA(W, L)
    landa = chi / norm(A, ord=2)

    conv_diff = 100
    old_C = 100
    i = 0
    while conv_diff > eps and i < max_iter:
        # Update L
        L = update_L(U, mu)
        # Update A
        A = computeA(W, L)
        M = np.eye(n_samples) + landa * A
        # Update U
        # U = np.dot(X, inv(M))
        U = solve(M, X)
        # Evaluate objective
        C = objective(X, U, W, L, landa, mu)
        print(C)
        conv_diff = np.abs(C - old_C)
        # Update landa and mu
        if i % 4 == 0:
            landa = chi / norm(A, ord=2)
            mu = max(mu / 2, delta / 2)

        # Keep iterating
        old_c = C
        i += 1
    return U


if __name__ == '__main__':
    from sklearn.datasets import load_iris
    iris = load_iris()
    X = iris.data[:, np.array([2, 3])]
    y = iris.target
    W = kneighbors_graph(X, n_neighbors=10)
    delta = 0.05
    U = RobustContinuousClustering(X, W, delta=delta)

    d = cdist(U, U)

    import matplotlib.pyplot as plt
    plt.scatter(X[:, 0], X[:, 1], c=y)
    plt.show()

    plt.scatter(U[:, 0], U[:, 1], c=y)
    plt.show()
