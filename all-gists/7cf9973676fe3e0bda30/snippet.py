# Author: Jean-Remi King <jeanremi.king@gmail.com>
"""
    Illustrate how a hinge loss and a log loss functions 
    typically used in SVM and Logistic Regression 
    respectively focus on a variable number of samples.
    For simplification purposes, we won't consider the
    regularization or penalty (C) factors.
"""
import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plt

np.random.seed(42)
# Setup data
# We'll try to fit the linear model y = w*X
n_sample, n_dim = 40, 2
X = np.random.randn(n_sample, n_dim)
coefs = np.random.randn(n_dim)  # set informative feature
y = np.sign(np.dot(X, coefs))  # add information to data
X += np.random.randn(n_sample, n_dim) / 2.  # add noise


def hinge(w, X, y):
    """Hinge loss, as used in SVM"""
    pred = np.dot(np.c_[X, np.ones(len(X))], w)
    loss = np.max([np.zeros_like(y), 1-pred*y], axis=0)
    return loss


def log(w, X, y):
    """Log loss, as used in logistic regression"""
    dist = np.dot(np.c_[X, np.ones(len(X))], w)
    return np.log2(1 + np.exp(-y * dist))


loss_funcs = dict(hinge=hinge, log=log)


def sum_loss(w, X, y, loss):
    """Sum losses across samples"""
    return np.sum(loss_funcs[loss](w, X, y))


def fit(X, y, loss, maxiter):
    """Optimization function to find w that minimize y-w*X"""
    from scipy.optimize import fmin
    np.random.seed(42)
    w0 = np.random.rand(X.shape[1] + 1)
    w = fmin(sum_loss, w0, args=(X, y, loss), maxiter=maxiter)
    return w


def plot(loss, ax, maxiter):
    # Fit
    w = fit(X, y, loss, maxiter)
    # Get individual losses
    losses = loss_funcs[loss](w, X, y)
    widths = losses / np.std(losses)

    # Plot data
    ax.scatter(X[:, 0], X[:, 1], s=widths*50, c='k', zorder=-1,
               edgecolor=None)
    ax.scatter(X[:, 0], X[:, 1], s=40, c=y,
               cmap=plt.cm.bwr, edgecolor=None)

    # Plot coef (line)
    coefs, intercept = w[:-1], w[-1]
    slope = -coefs[0] / coefs[1]
    xx = np.linspace(-2, 2)
    bb = -(intercept) / coefs[1]
    yy = slope * xx + bb
    ax.plot(xx, yy, 'k', linewidth=2)

    # Plot data distances to coef
    bb_ = X[:, 1] + X[:, 0] / slope
    xx_ = (bb_ - bb) / (slope + 1. / slope)
    yy_ = slope * xx_ + bb
    for ii in np.where(widths > 0)[0]:
        ax.plot([X[ii, 0], xx_[ii]], [X[ii, 1], yy_[ii]],
                linewidth=widths[ii]*2, color='k', zorder=-2)
    ax.legend()
    ax.set_aspect('equal')
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)

fig, axes = plt.subplots(1, 2, sharex=True, sharey=True,
                         figsize=[8., 4.], facecolor='w')


def animate(maxiter):
    axes[0].clear()
    axes[1].clear()
    for ax, loss in zip(axes, ['log', 'hinge']):
        plot(loss, ax, maxiter=maxiter)
        ax.set_title(loss)

ani = animation.FuncAnimation(fig, animate, range(1, 50),
                              blit=False, interval=100, repeat=True)
plt.show()
