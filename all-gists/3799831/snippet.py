import numpy as np
import FuncDesigner as fd
from openopt import NLP

from sklearn.metrics.pairwise import rbf_kernel, polynomial_kernel


def theta(x):
    return 0.5 * (fd.sign(x) + 1.)


# --- loss ---

class EpsilonInsensitiveLoss(object):

    def __init__(self, epsilon=0.1):
        self.epsilon = epsilon

    def __call__(self, y, y_pred):
        e = self.epsilon

        _y = y - y_pred

        low_x = (- _y - e)
        low  = low_x * theta(low_x)
        high_x = (_y - e)
        high = high_x * theta(high_x)

        return low + high


class L2Loss(object):

    def __call__(self, y, y_pred):
        return (y - y_pred) ** 2


class HuberQuantileLoss(object):

    def __init__(self, quantile=0.5):
        self.quantile = quantile

    def __call__(self, y, y_pred):
        q = self.quantile

        _y = y - y_pred

        mid  = (.5*_y**2 + (q - .5)*_y + .125) * theta(.5 - _y) * theta(_y + .5)
        low  = (_y * (q - 1))                  * theta(-.5 - _y)
        high = (_y * q)                        * theta(_y - .5)

        return mid + low + high



# --- kernel ---

class LinearKernel(object):

    def __call__(self, a, b):
        return np.dot(a, b.T)


class RBFKernel(object):

    def __init__(self, gamma=0.):
        self.gamma = gamma

    def __call__(self, a, b):
        return rbf_kernel(a, b, self.gamma)


class PolynomialKernel(object):

    def __init__(self, degree=2., gamma=0., coef0=1.):
        self.degree = degree
        self.gamma = gamma
        self.coef0 = coef0

    def __call__(self, a, b):
        return polynomial_kernel(a, b, self.degree, self.gamma, self.coef0)


# --- solver ---

class KernelModel(object):

    def __init__(self, X, kernel, beta, bias):
        self.kernel = kernel
        self.X = X
        self.beta = beta
        self.bias = bias

    def predict(self, X):
        return np.dot(self.kernel(X, self.X), self.beta) + self.bias


def fit_kernel_model(kernel, loss, X, y, gamma, weights=None):
    n_samples = X.shape[0]
    gamma = float(gamma)
    if weights is not None:
        weights = weights / np.sum(weights) * weights.size

    # --- optimize bias term ---

    bias = fd.oovar('bias', size=1)

    if weights is None:
        obj_fun = fd.sum(loss(y, bias))
    else:
        obj_fun = fd.sum(fd.dot(weights, loss(y, bias)))
    optimizer = NLP(obj_fun, {bias: 0.}, ftol=1e-6, iprint=-1)

    result = optimizer.solve('ralg')
    bias = result(bias)

    # --- optimize betas ---

    beta = fd.oovar('beta', size=n_samples)

    # gram matrix
    K = kernel(X, X)
    assert K.shape == (n_samples, n_samples)

    K_dot_beta = fd.dot(K, beta)

    penalization_term = gamma * fd.dot(beta, K_dot_beta)
    if weights is None:
        loss_term = fd.sum(loss(y - bias, K_dot_beta))
    else:
        loss_term = fd.sum(fd.dot(weights, loss(y - bias, K_dot_beta)))
    obj_fun = penalization_term + loss_term

    beta0 = np.zeros((n_samples,))

    optimizer = NLP(obj_fun, {beta: beta0}, ftol=1e-4, iprint=-1)
    result = optimizer.solve('ralg')
    beta = result(beta)

    return KernelModel(X, kernel, beta, bias)
