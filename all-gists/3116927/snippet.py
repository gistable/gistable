"""
Three ways of computing the Hellinger distance between two discrete
probability distributions using NumPy and SciPy.
"""

import numpy as np
from scipy.linalg import norm
from scipy.spatial.distance import euclidean


_SQRT2 = np.sqrt(2)     # sqrt(2) with default precision np.float64


def hellinger1(p, q):
    return norm(np.sqrt(p) - np.sqrt(q)) / _SQRT2


def hellinger2(p, q):
    return euclidean(np.sqrt(p), np.sqrt(q)) / _SQRT2


def hellinger3(p, q):
    return np.sqrt(np.sum((np.sqrt(p) - np.sqrt(q)) ** 2)) / _SQRT2