import numpy as np
from math import exp, log

"""
SGD for logistic loss + factorization machines
The code follows this paper:
[1] http://www.ics.uci.edu/~smyth/courses/cs277/papers/factorization_machines_with_libFM.pdf
"""

def sigmoid(x):
    if x > 500:
        return 1
    elif x < -500:
        return 0
    return 1 / (1 + exp(-x))


def log_loss(y, p):
    z = p * y
    if z > 18:
        return exp(-z)
    if z < -18:
        return -z
    return -log(sigmoid(z))


class FM(object):

    def __init__(self, etha=0.01, l=0.01, sigma=0.001, n_iter=1000, k=3):
        # TODO: default parameters
        self.etha = etha
        self.l = l
        self.sigma = sigma
        self.n_iter = n_iter
        self.k = k
        self.w0 = 0
        self.n = 0
        self.p = 0
        self.w = None
        self.v = None

    def fit(self, X, Y, verbose=True):
        self.n, self.p = X.shape
        self.w = np.zeros(self.p)
        self.v = self.sigma * np.array(np.random.randn(self.p, self.k))

        for epoch in range(self.n_iter):

            for x, y in zip(X, Y):
                p = self._predict(x)
                delta = y * (sigmoid(y * p) - 1.0)
                self.w0 -= self.etha * (delta + 2 * self.l * self.w0)
                for i in range(self.p):
                    self.w[i] -= self.etha *\
                                 (delta * x[i] + 2 * self.l * self.w[i])
                    for j in range(self.k):
                        h = x[i] *\
                            (np.dot(self.v[:, j], x) - x[i] * self.v[i, j])
                        self.v[i, j] -= self.etha *\
                                        (delta * h + 2 * self.l * self.v[i, j])
            if verbose:
                print(self.test(X, Y))

        return self

    def _predict(self, x):
        res = self.w0 + np.dot(self.w, x)
        f_res = 0.0
        # [1] equation 5
        for f in range(self.k):
            s = 0.0
            s_squared = 0.0
            for j in range(self.p):
                el = self.v[j, f] * x[j]
                s += el
                s_squared += el ** 2
            f_res += 0.5 * (s ** 2 - s_squared)
        res += f_res
        return res

    def predict(self, X):
        return np.array([self._predict(x) for x in X])

    def scale(self, Y):
        return np.array([sigmoid(y) for y in Y])

    def test(self, X, Y):
        return np.mean([log_loss(p, y) for p, y in zip(self.predict(X), Y)])


def main():
    fm = FM()
    X_train = np.array([[2., 1., 1., 0., 1., 1., 0., 0., 0.],
                [2., 1., 1., 1., 0., 0., 1., 0., 0.],
                [2., 1., 1., 0., 0., 0., 0., 1., 0.],
                [2., 1., 0., 0., 0., 0., 0., 0., 1.],
                [4., 2., 0., 0., 0., 0., 0., 0., 1.],
                [4., 2., 0., 0., 0., 0., 0., 0., 1.],
                [4., 2., 0., 0., 0., 0., 0., 0., 1.]])
    Y_train = np.array([1, 1, -1, -1, 1, 1, 1])
    fm.fit(X_train, Y_train)
    print(fm.scale(fm.predict(X_train)))


if __name__ == "__main__":
    main()