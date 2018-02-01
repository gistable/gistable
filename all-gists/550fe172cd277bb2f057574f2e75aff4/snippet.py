import numpy as np
from scipy.linalg import blas
from scipy.ndimage import zoom

# Machine epsilon for float32
EPS = np.finfo(np.float32).eps


# pylint: disable=no-member
def dot(x, y):
    """Returns the dot product of two float32 arrays with the same shape."""
    return blas.sdot(x.ravel(), y.ravel())


# pylint: disable=no-member
def axpy(a, x, y):
    """Sets y = a*x + y for float a and float32 arrays x, y and returns y."""
    y_ = blas.saxpy(x.ravel(), y.ravel(), a=a).reshape(y.shape)
    if y is not y_:
        y[:] = y_
    return y


def resize(arr, size, order=1):
    """Resamples a CxHxW NumPy float array to a different HxW shape."""
    h, w = size
    resized_arr = zoom(arr, (1, h/arr.shape[1], w/arr.shape[2]), order=order, mode='wrap')
    assert resized_arr.shape[1:] == size
    return resized_arr


def roll2(arr, xy):
    """Translates an array by the shift xy, wrapping at the edges."""
    if (xy == 0).all():
        return arr
    return np.roll(np.roll(arr, xy[0], -1), xy[1], -2)


class DMSQNOptimizer:
    """Implements an experimental Quasi-Newton optimizer that incorporates Hessian damping,
    momentum, per-feature learning rate scaling, and iterate averaging."""
    def __init__(self, params, step_size=2, averaging=True, avg_decay=3, n_corr=10, b1=0.75,
                 phi=0.2):
        """Initializes the optimizer."""
        self.params = params
        self.step_size = step_size
        self.averaging = averaging
        assert avg_decay >= 0
        self.avg_decay = avg_decay
        self.n_corr = n_corr
        self.b1 = b1
        self.phi = phi

        self.step = 0
        self.xy = np.zeros(2, dtype=np.int32)
        self.grad = None
        self.g1 = np.zeros_like(params)
        self.g2 = np.zeros_like(params) + EPS
        self.p1 = params.copy()
        self.sk = []
        self.yk = []

    def update(self, opfunc):
        """Returns a step's parameter update given a loss/gradient evaluation function."""
        self.step += 1

        if self.step == 1:
            _, self.grad = opfunc(self.params)
            self.g1 *= self.b1
            self.g1 += self.grad
            self.g2 += self.grad**2

        # Compute step, loss, and gradient
        self.g1 *= self.b1
        s = -self.step_size * self.inv_hv(self.g1 + self.grad)
        self.params += s
        loss, grad = opfunc(self.params)
        self.g1 += grad
        self.g2 += grad**2

        # Store curvature pair and gradient
        y = (1 - self.phi) * (grad - self.grad)
        axpy(self.phi, s, y)
        y *= np.sqrt(self.g2)
        self.store_curvature_pair(s, y)
        self.grad = grad

        # Polynomial-decay averaging
        weight = (1 + self.avg_decay) / (self.step + self.avg_decay)
        self.p1 *= 1 - weight
        axpy(weight, self.params, self.p1)
        if self.averaging:
            return self.p1, loss
        else:
            return self.params, loss

    def store_curvature_pair(self, s, y):
        """Updates the L-BFGS memory with a new curvature pair."""
        self.sk.append(s)
        self.yk.append(y)
        if len(self.sk) > self.n_corr:
            self.sk, self.yk = self.sk[1:], self.yk[1:]

    def inv_hv(self, p):
        """Computes the product of a vector with an approximation of the inverse Hessian."""
        p = p.copy()
        alphas = []
        for s, y in zip(reversed(self.sk), reversed(self.yk)):
            alphas.append(dot(s, p) / dot(s, y))
            axpy(-alphas[-1], y, p)

        if len(self.sk) > 0:
            s, y = self.sk[-1], self.yk[-1]
            p *= dot(s, y) / dot(y, y)
        else:
            p /= np.sqrt(self.g2)

        for s, y, alpha in zip(self.sk, self.yk, reversed(alphas)):
            beta = dot(y, p) / dot(s, y)
            axpy(alpha - beta, s, p)

        return p

    def roll(self, xy):
        """Rolls the optimizer's internal state."""
        if (xy == 0).all():
            return
        self.xy += xy
        if self.grad is not None:
            self.grad[:] = roll2(self.grad, xy)
        self.g1[:] = roll2(self.g1, xy)
        self.g2[:] = roll2(self.g2, xy)
        self.p1[:] = roll2(self.p1, xy)
        for i in range(len(self.sk)):
            self.sk[i][:] = roll2(self.sk[i], xy)
            self.yk[i][:] = roll2(self.yk[i], xy)

    def set_params(self, last_iterate):
        """Sets params to the supplied array, partially clearing the optimizer's internal state."""
        self.step = 0
        self.params = last_iterate
        self.grad = None
        xy = self.params.shape[-2:]
        self.g1 = resize(self.g1, xy)
        self.g2 = np.maximum(resize(self.g2, xy), EPS) * (self.g2.size / last_iterate.size)
        self.p1 = np.zeros_like(last_iterate)
        self.sk = []
        self.yk = []

    def restore_state(self, optimizer):
        """Given a DMSQNOptimizer instance, restores internal state from it."""
        assert isinstance(optimizer, DMSQNOptimizer)
        self.params = optimizer.params
        self.grad = optimizer.grad
        self.g1 = optimizer.g1
        self.g2 = optimizer.g2
        self.p1 = optimizer.p1
        self.sk = optimizer.sk
        self.yk = optimizer.yk
        self.step = optimizer.step
        self.xy = optimizer.xy.copy()
        self.roll(-self.xy)
