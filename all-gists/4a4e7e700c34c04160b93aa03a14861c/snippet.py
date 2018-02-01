# Efficient passive aggressive updates for multi-class classification
#
# Original article:
# "Column squishing for multiclass updates"
# https://nlpers.blogspot.com/2017/08/column-squishing-for-multiclass-updates.html


from __future__ import division
import numpy as np
import scipy.optimize


def multiclass_update(A, w, j):
    """Given matrix A in R^{k x d}), w in R^d) and j, find B that solves:

       min_B ||B-A||^2 st (w B)_j >= (w B)_i + 1 for all i != j

    observe that any change will be in the direction of x

    so compute scalars:
      C_i = [ a_i - a_j + 1 ] / ||x||^2

    where a_i is x*A[i,:]

    """
    k, d = A.shape
    a = A.dot(w)
    C = (a - a[j] + 1) / w.dot(w)
    C[j] = 0
    delta = min_delta(C, j)
    return A + delta.reshape((k,1)).dot(w.reshape(1, d))


def slow(A, w, j):
    # Here's a slow version of the same problem, which uses a less-efficient
    # numerical method to find the solution.

    # min_B ||B-A||^2 st (w B)_j >= (w B)_i + 1 for all i != j

    [k, d] = A.shape

    def f(x):
        B = x.reshape((k,d))
        D = (B - A).flatten()
        return 0.5*D.dot(D), D

    def h(x):
        # inequality constraints
        B = x.reshape((k,d))
        s = B.dot(w)
        H = (s[j] - s - 1)
        H[j] = 0
        return H

    # precompute Jacobian of constraints
    J = np.zeros((k,d,k))
    for i in range(k):
        if i != j:
            J[i,:,i] -= w
            J[j,:,i] += w
    J = J.reshape((k*d,k)).T

    def h_jac(_):
        return J

    if 0:
        from arsenal.math import spherical, compare
        x = A.flatten()
        eps = 1e-5
        m = 100
        fd = np.zeros(m)
        ad = np.zeros(m)
        for t in range(m):
            y = spherical(k*d)
            z = spherical(k)
            fd[t] = (h(x + eps*y).dot(z) - h(x - eps*y).dot(z)) / (2*eps)
            ad[t] = y.dot((h_jac(x).T.dot(z)).flatten())
            compare(fd, ad).show()

    return scipy.optimize.minimize(f, x0 = A, jac=1,
                                   constraints={'type': 'ineq', 'fun': h, 'jac': h_jac}).x


def min_delta(C, j):
    # solve:
    #   min_delta sum_i delta_i^2 st delta_j >= delta_i + C_i for i != j
    # do a change of variables where
    #   z = delta + D
    # then we want to solve
    #   min_x ||x-z|| st x_j >= x_i for i != j
    # after reordering C so that D[0] = C[j] and D[1:] is sorted(C[!j])
    # and then need to un-sort the results
    order = (-C).argsort()
    j_idx = (order == j).nonzero()[0][0]
    order2 = np.concatenate([[j], order[:j_idx], order[j_idx+1:]])
    proj = column_squishing(C[order2], False)
    return proj[order2.argsort()] - C


def column_squishing(z, do_proj=True):
    # input: z has z_2 >= z_3 >= z_4 >= ... >= z_n
    # returns the projection of z into { x in R : 0 <= x_i <= x_1 <= 1 }
    # this is algorithm 5 from:
    #   Factoring nonnegative matrices with linear programs
    #   by Bittorf et al., June 2012
    #   http://pages.cs.wisc.edu/~brecht/papers/12.Bit.EtAl.HOTT.pdf
    proj01 = (lambda a: max(0, min(1, a))) if do_proj else (lambda a: a)
    proj0_ = (lambda a: max(0, a)) if do_proj else (lambda a: a)
    n = z.shape[0]
    assert len(z.shape) == 1
    assert all([z[i] >= z[i+1] for i in xrange(1, n-1)])
    mu = z[0]
    kc = n-1
    for k in range(1, n):
        if z[k] <= proj01(mu):
            kc = k - 1
            break
        mu = mu * k / (k+1) + z[k] / (k+1)
    x = np.zeros(n) + proj01(mu)
    for k in range(kc+1, n):
        x[k] = proj0_(z[k])
    return x


import seaborn
import pandas as pd
import pylab as pl
from arsenal.timer import timers
from arsenal import iterview
from arsenal.math import assert_equal

def main():

    T = timers()

    R = 10  # repetitions
    ks = range(3, 120, 10) * R
    np.random.shuffle(ks)

    for k in iterview(ks):
        i = np.random.randint(k)

        d = 5
        A = np.random.randn(k,d)
        w = np.random.randn(d)

        with T['fast'](k=k):
            a = multiclass_update(A, w, i)

        with T['slow'](k=k):
            b = slow(A, w, i)

        assert_equal(a.flatten(), b.flatten())

        s = a.dot(w)
        assert s.argmax() == i # `i` should win.
        s = np.sort(s)
        margin = s[-1] - s[-2]
        assert margin >= 0.99999

    T.plot_feature('k', show='scatter')
    pl.show()

if __name__ == '__main__':
    main()
