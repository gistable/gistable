#! /usr/bin/env python

import sys
import random
import pymc
import numpy
from dendropy.mathlib import probability as prob
from dendropy.mathlib import statistics as stats

rng = random.Random()

##############################################################################
# supporting functions

def summarize(mcmc, field):
    results = mcmc.trace(field)[:]
    results = zip(*results)
    means = []
    for r in results:
        m, v = stats.mean_and_sample_variance(r)
        means.append(m)
    means.append(1.0 - sum(means))
    print
    print "---"
    print means

##############################################################################
# data

NUM_DRAWS = 100
NUM_SAMPLES = 50
TRUE_PROPS = [0.6, 0.3, 1.0]

def generate_data():
    data = []
    for i in range(NUM_SAMPLES):
        x = numpy.random.multinomial(NUM_DRAWS, TRUE_PROPS)
        data.append(x)
    return data

##############################################################################
# model

props = pymc.Dirichlet(
        name="props",
        theta=[1.0, 1.0, 1.0],)
draws = pymc.Multinomial(
        name="draws",
        value=generate_data(),
        n=NUM_DRAWS,
        p=props,
        observed=True)
mcmc = pymc.MCMC([props, draws])
mcmc.sample(iter=100000, burn=10000, thin=100)
# mcmc.sample(iter=1000, burn=100, thin=1)
summarize(mcmc, "props")







