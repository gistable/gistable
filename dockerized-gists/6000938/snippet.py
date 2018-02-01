#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function
import emcee
import numpy as np
import matplotlib.pyplot as pl

np.random.seed(123)

# Define the model.
def model(p):
    m, b = p
    return lambda x0: m * x0 + b

# Define the posterior probability function (assuming flat priors).
def lnprobfn(p, xhat, yhat, yerr, xerr):
    p, x = p[:2], p[2:]
    y = model(p)(x)
    return -0.5 * (np.sum(((yhat - y) / yerr) ** 2) +
                   np.sum(((xhat - x) / xerr) ** 2))

# Generate data.
truth = [1.5, 4.]
N = 30
x_true = 50 * np.random.rand(N)
y_true = model(truth)(x_true)

# "Observe" the data.
xerr, yerr = 2.0, 2.0
x_obs = x_true + xerr * np.random.randn(N)
y_obs = y_true + yerr * np.random.randn(N)

# Set up the sampler.
nwalkers, ndim = 100, N + 2
p0 = np.append(truth, x_obs)
p0 = [p0 + np.random.randn(ndim) for i in range(nwalkers)]
sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprobfn,
                                args=[x_obs, y_obs, xerr, yerr])

# Burn in.
print("Burning in.")
p0, lnprob0, state = sampler.run_mcmc(p0, 500)
sampler.reset()

# Sample.
print("Sampling.")
sampler.run_mcmc(p0, 1000)

# Print results.
samples = sampler.flatchain
print("m = {0} ± {1}".format(np.mean(samples[:, 0]), np.std(samples[:, 0])))
print("b = {0} ± {1}".format(np.mean(samples[:, 1]), np.std(samples[:, 1])))

# Plot results.
fig = pl.figure(figsize=(10, 5))

ax1 = fig.add_subplot(121)
ax1.hist(samples[:, 0], 50, histtype="step", color="k")
ax1.axvline(truth[0])
ax1.set_yticklabels([])
ax1.set_xlabel("$m$")

ax2 = fig.add_subplot(122)
ax2.hist(samples[:, 1], 50, histtype="step", color="k")
ax2.axvline(truth[1])
ax2.set_yticklabels([])
ax2.set_xlabel("$b$")
fig.savefig("line.png")