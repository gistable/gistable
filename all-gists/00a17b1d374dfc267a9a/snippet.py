"""
Implementations of:

    Probabilistic Matrix Factorization (PMF) [1],
    Bayesian PMF (BPMF) [2],
    Modified BPFM (mBPMF)

using `pymc3`. mBPMF is, to my knowledge, my own creation. It is an attempt
to circumvent the limitations of `pymc3` w/regards to the Wishart distribution:

    https://github.com/pymc-devs/pymc3/commit/642f63973ec9f807fb6e55a0fc4b31bdfa1f261e

[1]  http://papers.nips.cc/paper/3208-probabilistic-matrix-factorization.pdf
[2]  https://www.cs.toronto.edu/~amnih/papers/bpmf.pdf

"""
import sys
import time
import logging

import pymc3 as pm
import numpy as np
import pandas as pd
import theano
import theano.tensor as t
import scipy as sp


DATA_NOT_FOUND = -1


# data from: https://gist.github.com/macks22/b40ac9c685e920ad3ca2
def read_jester_data(fname='jester-dense-subset-100x20.csv'):
    """Read dense Jester dataset and split train/test data randomly.
    We use a 0.9:0.1 Train:Test split.
    """
    logging.info('reading data')
    try:
        data = pd.read_csv(fname)
    except IOError as err:
        print str(err)
        url = 'https://gist.github.com/macks22/b40ac9c685e920ad3ca2'
        print 'download from: %s' % url
        sys.exit(DATA_NOT_FOUND)

    # Calculate split sizes.
    logging.info('splitting train/test sets')
    n, m = data.shape           # # users, # jokes
    N = n * m                   # # cells in matrix
    test_size = N / 10          # use 10% of data as test set
    train_size = N - test_size  # and remainder for training

    # Prepare train/test ndarrays.
    train = data.copy().values
    test = np.ones(data.shape) * np.nan

    # Draw random sample of training data to use for testing.
    tosample = np.where(~np.isnan(train))        # only sample non-missing values
    idx_pairs = zip(tosample[0], tosample[1])    # zip row/col indices
    indices = np.arange(len(idx_pairs))          # indices of row/col index pairs
    sample = np.random.choice(indices, replace=False, size=test_size)  # draw sample

    # Transfer random sample from train set to test set.
    for idx in sample:
        idx_pair = idx_pairs[idx]         # retrieve sampled index pair
        test[idx_pair] = train[idx_pair]  # transfer to test set
        train[idx_pair] = np.nan          # remove from train set

    # Verify everything worked properly
    assert(np.isnan(train).sum() == test_size)
    assert(np.isnan(test).sum() == train_size)

    # Return the two numpy ndarrays
    return train, test


def build_pmf_model(train, alpha=2, dim=10, std=0.01):
    """Construct the Probabilistic Matrix Factorization model using pymc3.
    Note that the `testval` param for U and V initialize the model away from
    0 using a small amount of Gaussian noise.

    :param np.ndarray train: Training data (observed) to learn the model on.
    :param int alpha: Fixed precision to use for the rating likelihood function.
    :param int dim: Dimensionality of the model; rank of low-rank approximation.
    :param float std: Standard deviation for Gaussian noise in model initialization.
    """
    # Mean value imputation on training data.
    train = train.copy()
    nan_mask = np.isnan(train)
    train[nan_mask] = train[~nan_mask].mean()

    # Low precision reflects uncertainty; prevents overfitting.
    # We use point estimates from the data to intialize.
    # Set to mean variance across users and items.
    alpha_u = 1 / train.var(axis=1).mean()
    alpha_v = 1 / train.var(axis=0).mean()

    logging.info('building the PMF model')
    n, m = train.shape
    with pm.Model() as pmf:
        U = pm.MvNormal(
            'U', mu=0, tau=alpha_u * np.eye(dim),
            shape=(n, dim), testval=np.random.randn(n, dim) * std)
        V = pm.MvNormal(
            'V', mu=0, tau=alpha_v * np.eye(dim),
            shape=(m, dim), testval=np.random.randn(m, dim) * std)
        R = pm.Normal(
            'R', mu=t.dot(U, V.T), tau=alpha * np.ones(train.shape),
            observed=train)

    logging.info('done building PMF model')
    return pmf


def build_bpmf_model(train, alpha=2, dim=10, std=0.01):
    """Build the original BPMF model, which we cannot sample from due to
    current limitations in pymc3's implementation of the Wishart distribution.
    """
    n, m = train.shape
    beta_0 = 1  # scaling factor for lambdas; unclear on its use

    # Mean value imputation on training data.
    train = train.copy()
    nan_mask = np.isnan(train)
    train[nan_mask] = train[~nan_mask].mean()

    logging.info('building the BPMF model')
    with pm.Model() as bpmf:
        # Specify user feature matrix
        lambda_u = pm.Wishart(
            'lambda_u', n=dim, V=np.eye(dim), shape=(dim, dim),
            testval=np.random.randn(dim, dim) * std)
        mu_u = pm.Normal(
            'mu_u', mu=0, tau=beta_0 * lambda_u, shape=dim,
            testval=np.random.randn(dim) * std)
        U = pm.MvNormal(
            'U', mu=mu_u, tau=lambda_u, shape=(n, dim),
            testval=np.random.randn(n, dim) * std)

        # Specify item feature matrix
        lambda_v = pm.Wishart(
            'lambda_v', n=dim, V=np.eye(dim), shape=(dim, dim),
            testval=np.random.randn(dim, dim) * std)
        mu_v = pm.Normal(
            'mu_v', mu=0, tau=beta_0 * lambda_v, shape=dim,
             testval=np.random.randn(dim) * std)
        V = pm.MvNormal(
            'V', mu=mu_v, tau=lambda_v, shape=(m, dim),
            testval=np.random.randn(m, dim) * std)

        # Specify rating likelihood function
        R = pm.Normal(
            'R', mu=t.dot(U, V.T), tau=alpha * np.ones((n, m)),
            observed=train)

    logging.info('done building the BPMF model')
    return bpmf


def build_mod_bpmf_model(train, alpha=2, dim=10, std=0.01):
    """Build the modified BPMF model using pymc3. The original model uses
    Wishart priors on the covariance matrices. Unfortunately, the Wishart
    distribution in pymc3 is currently not suitable for sampling. This
    version decomposes the covariance matrix into:

        diag(sigma) \dot corr_matrix \dot diag(std).

    We use uniform priors on the standard deviations (sigma) and LKJCorr
    priors on the correlation matrices (corr_matrix):

        sigma ~ Uniform
        corr_matrix ~ LKJCorr(n=1, p=dim)

    """
    n, m = train.shape
    beta_0 = 1  # scaling factor for lambdas; unclear on its use

    # Mean value imputation on training data.
    train = train.copy()
    nan_mask = np.isnan(train)
    train[nan_mask] = train[~nan_mask].mean()

    # We will use separate priors for sigma and correlation matrix.
    # In order to convert the upper triangular correlation values to a
    # complete correlation matrix, we need to construct an index matrix:
    n_elem = dim * (dim - 1) / 2
    tri_index = np.zeros([dim, dim], dtype=int)
    tri_index[np.triu_indices(dim, k=1)] = np.arange(n_elem)
    tri_index[np.triu_indices(dim, k=1)[::-1]] = np.arange(n_elem)

    logging.info('building the BPMF model')
    with pm.Model() as bpmf:
        # Specify user feature matrix
        sigma_u = pm.Uniform('sigma_u', shape=dim)
        corr_triangle_u = pm.LKJCorr(
            'corr_u', n=1, p=dim,
            testval=np.random.randn(n_elem) * std)

        corr_matrix_u = corr_triangle_u[tri_index]
        corr_matrix_u = t.fill_diagonal(corr_matrix_u, 1)
        cov_matrix_u = t.diag(sigma_u).dot(corr_matrix_u.dot(t.diag(sigma_u)))
        lambda_u = t.nlinalg.matrix_inverse(cov_matrix_u)

        mu_u = pm.Normal(
            'mu_u', mu=0, tau=beta_0 * t.diag(lambda_u), shape=dim,
             testval=np.random.randn(dim) * std)
        U = pm.MvNormal(
            'U', mu=mu_u, tau=lambda_u, shape=(n, dim),
            testval=np.random.randn(n, dim) * std)

        # Specify item feature matrix
        sigma_v = pm.Uniform('sigma_v', shape=dim)
        corr_triangle_v = pm.LKJCorr(
            'corr_v', n=1, p=dim,
            testval=np.random.randn(n_elem) * std)

        corr_matrix_v = corr_triangle_v[tri_index]
        corr_matrix_v = t.fill_diagonal(corr_matrix_v, 1)
        cov_matrix_v = t.diag(sigma_v).dot(corr_matrix_v.dot(t.diag(sigma_v)))
        lambda_v = t.nlinalg.matrix_inverse(cov_matrix_v)

        mu_v = pm.Normal(
            'mu_v', mu=0, tau=beta_0 * t.diag(lambda_v), shape=dim,
             testval=np.random.randn(dim) * std)
        V = pm.MvNormal(
            'V', mu=mu_v, tau=lambda_v, shape=(m, dim),
            testval=np.random.randn(m, dim) * std)

        # Specify rating likelihood function
        R = pm.Normal(
            'R', mu=t.dot(U, V.T), tau=alpha * np.ones((n, m)),
            observed=train)

    logging.info('done building the BPMF model')
    return bpmf


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s]: %(message)s')

    # Read data and build PMF model.
    train, test = read_jester_data()
    pmf = build_pmf_model(train)

    # Find mode of posterior using optimization
    with pmf:
        tstart = time.time()
        logging.info('finding PMF MAP using Powell optimization')
        start = pm.find_MAP(fmin=sp.optimize.fmin_powell)
        elapsed = time.time() - tstart
        logging.info('found PMF MAP in %d seconds' % int(elapsed))

    # Build the modified BPMF model using same default params as PMF.
    mod_bpmf = build_mod_bpmf_model(train)

    # Use PMF MAP to initialize sampling for modified BPMF.
    for key in mod_bpmf.test_point:
        if key not in start:
            start[key] = mod_bpmf.test_point[key]

    # Attempt to sample with modified BPMF
    # (this part raises PositiveDefiniteError when using the normal BPMF model).
    with mod_bpmf:
        nsamples = 100
        njobs = 2
        logging.info(
            'drawing %d MCMC samples using %d jobs' % (nsamples, njobs))
        step = pm.NUTS(scaling=start)
        trace = pm.sample(nsamples, step, start=start, njobs=njobs)