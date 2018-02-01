#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File: stratified.py
Author: SpaceLis
Email: Wen.Li@tudelft.nl
Github: http://github.com/spacelis
Description:
    Sampling in a stratified way. That is sampling from each subpopulation to
    make the sample set more representative than simple random sampling. For
    example, a population of places from each category is not uniform, it is
    needed to insure each category has a place sampled and the number of the
    samples from each category should be propotional to its size.
"""


import numpy as np
from itertools import tee, izip, chain
from collections import Counter


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)


def int_partition(K, percentages, minimum=1):
    """ Scale the percentages up K times
    """
    assert K > minimum * len(percentages), 'K is too small for partitioning'
    p = np.array(percentages, dtype=np.float)
    dist = np.ones(len(p), dtype=np.int) * minimum
    dist += (K - len(p)) * p
    left = K - dist.sum()
    if left > 0:
        while left > 0:
            diff = p * K - dist
            dist[np.argmax(diff)] += 1
            left -= 1
    elif left < 0:   # FIXME seems never having chance to run actually
        while left < 0:
            diff = p * K - dist
            dist[np.argmin(diff)] -= 1
            left += 1
    return dist


def stratified_samples(iterable, percentages, size, prop_sizes=True):
    """ Sampling the data with stratified sampling
    """
    partitions = len(percentages)
    dist = sorted(Counter(iterable).iteritems(),
                  key=lambda x: x[1],
                  reverse=True)
    if prop_sizes:
        samplesize = int_partition(size, percentages)
    else:
        samplesize = int_partition(size,
                                   [1. / partitions] * partitions)
    pivots = list(np.cumsum(int_partition(len(dist), percentages)))
    chozen_idx = [np.random.choice(range(s, t), n, replace=False)
            for n, (s, t) in zip(samplesize, pairwise([0] + pivots))]
    chozen = [[dist[i][0] for i in ig] for ig in chozen_idx]
    return chozen