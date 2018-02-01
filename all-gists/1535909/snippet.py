from numpy.random import uniform
import numpy
import random

def slice_sampler(px, N = 1, x = None):
    """
    Provides samples from a user-defined distribution.
    
    slice_sampler(px, N = 1, x = None)
    
    Inputs:
    px = A discrete probability distribution.
    N  = Number of samples to return, default is 1
    x  = Optional list/array of observation values to return, where prob(x) = px.

    Outputs:
    If x=None (default) or if len(x) != len(px), it will return an array of integers
    between 0 and len(px)-1. If x is supplied, it will return the
    samples from x according to the distribution px.    
    """
    values = numpy.zeros(N, dtype=numpy.int)
    samples = numpy.arange(len(px))
    px = numpy.array(px) / (1.*sum(px))
    u = uniform(0, max(px))
    for n in xrange(N):
        included = px>=u
        choice = random.sample(range(numpy.sum(included)), 1)[0]
        values[n] = samples[included][choice]
        u = uniform(0, px[included][choice])
    if x:
        if len(x) == len(px):
            x=numpy.array(x)
            values = x[values]
        else:
            print "px and x are different lengths. Returning index locations for px."
    if N == 1:
        return values[0]
    return values
