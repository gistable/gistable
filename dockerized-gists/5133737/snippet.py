"""
Some python code for
Markov Chain Monte Carlo and Gibs sampling
by Bruce Walsh
"""


import numpy as np
import numpy.linalg as npla


def gaussian(x, sigma, sampled=None):
    """

    """
    if sampled is None:
        L = npla.cholesky(sigma)
        z = np.random.randn(x.shape[0], 1)
        return np.dot(L, z+x)
    else:
        return np.exp(-0.5*np.dot( (x-sampled).T, np.dot(npla.inv(sigma), (x-sampled))))[0,0]


def gaussian_1d(x, sigma, sampled=None):
    """
    1d Gaussian
    """
    if sampled is None:
        return sigma*np.random.randn(1)[0]
    else:
        return np.exp(-0.5( (x-sampled)**2)/sigma**2)


def chi_sq(x, sampled = None, n = 0):
    """
    chi squared function. Adapted for
    usage in metropolis-hastings.
    """
    if sampled is None:
        return np.random.chisquare(n)
    else:
        return np.power(sampled,0.5*n - 1)*np.exp(-0.5*sampled)


def inv_chi_sq(theta, n, a):
    """
    scaled inverse chi squared function.
    """
    return np.power(theta, -0.5*n)*np.exp(-a/(2*theta))


def metropolis(f, proposal, old):
    """
    basic metropolis algorithm, according to the original,
    (1953 paper), needs symmetric proposal distribution.
    """
    new = proposal(old)
    alpha = np.min([f(new)/f(old), 1])
    u = np.random.uniform()
    # _cnt_ indicates if new sample is used or not.
    cnt = 0
    if (u < alpha):
        old = new
        cnt = 1
    return old, cnt


def met_hast(f, proposal, old):
    """
    metropolis_hastings algorithm.
    """
    new = proposal(old)
    alpha = np.min([(f(new)*proposal(new, sampled = old))/(f(old) * proposal(old, sampled = new)), 1])
    u = np.random.uniform()
    cnt = 0
    if (u < alpha):
        old = new
        cnt = 1
    return old, cnt

def run_chain(chainer, f, proposal, start, n, take=1):
    """
    _chainer_ is one of Metropolis, MH, Gibbs ...
    _f_ is the unnormalized density function to sample
    _proposal_ is the proposal distirbution
    _start_ is the initial start of the Markov Chain
    _n_ length of the chain
    _take_ thinning
    """
    count = 0
    samples = [start]
    for i in range(n):
        start, c = chainer(f, proposal, start)
        count = count + c
        if i%take is 0:
            samples.append(start)
    return samples, count

def uni_prop(x, frm, to, sampled=None):
    """
    a uniform proposal generator --
    is symmetric!
    """
    return np.random.uniform(frm, to)


#
#how to use:
# from functools import partial
# import pylab
# from mcmc *
# # MCMC and Gibbs Sampling, by Walsh, 2004, p.8
# # proposal dist. is uniform (symmetric) -> metropolis
# f = partial(inv_chi_sq, n = 5, a = 4)
# prop = partial(uni_prop, frm=0, to = 100)
# smpls = run_chain(metropolis, f, prop, 1, 500)
# pylab.plot(smpls[0])
#
# # MCMC and Gibbs Sampling, Walsh, p. 9
# f = partial(inv_chi_sq, n = 5, a = 4)
# prop = partial(chi_sq, n=1))
# smpls = run_chain(metropolis, f, prop, 1, 500)
# pylab.plot(smpls[0])
##