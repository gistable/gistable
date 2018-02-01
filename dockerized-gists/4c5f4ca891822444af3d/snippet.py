"""Lanczos interpolation (resampling): 1D.

Written by Michael Wood-Vasey 
based on https://en.wikipedia.org/wiki/Lanczos_resampling
"""
from __future__ import division, print_function

import numpy as np

def lanczos_kernel(x, order):
    return np.sinc(x) * np.sinc(x/order) * ((x > -order) * (x < order))

def lanczos_interpolate(x, samples, order):
    if np.isscalar(x):
        x_arr = [x]
        return_scalar = True
    else:
        x_arr = x
        return_scalar = False

    nx = len(samples)
    result = np.zeros_like(x_arr)
    # Written this way to support non-scalar x.
    for i, x in enumerate(x_arr):
        i_min, i_max = int(np.floor(x) - order +1), int(np.floor(x) + order)
        i_min, i_max = max(i_min, 0), min(i_max, nx)
        window = np.arange(i_min, i_max)
        result[i] = np.sum(samples[window] * lanczos_kernel(x - window, order))

    if return_scalar:
        return result[0]
    else:
        return result

def shift_lanczos(x, samples, shift, order):
    return lanczos_interpolate(x+shift, samples, order)
####

from nose.tools import raises, assert_equal
from numpy.testing import assert_allclose, assert_array_almost_equal_nulp

@raises(ZeroDivisionError)
def test_lanczos_kernel_divide_by_zero():
    lanczos_kernel(1, 0)

def test_lanczos_kernel_zero():
    expected = 1
    observed = lanczos_kernel(0, 1)
    assert_equal(expected, observed)

def test_lanczos_kernel_out_of_window():
    expected = 0
    observed = lanczos_kernel(2, 1)
    assert_equal(expected, observed)

def test_lanczos_kernel_array_a2():
    x = np.array([-2, -1.5, -1, 0., +1, +1.5, +2])
    expected = np.array([0, -0.063684352027861824, 0, 1, 0, -0.063684352027861824, 0])
    observed = lanczos_kernel(x, order=2)
    print(repr(expected), repr(observed))
    assert_allclose(expected, observed, atol=1e-9)

def test_lanczos_kernel_array_a3():
    x = np.array([-3, -2.5, -2, -1.5, -1, 0., +1, +1.5, +2, +2.5, +3])
    expected = np.array([0, 0.024317084074161062, 0, -0.13509491152311703, 0, 1, 0, -0.13509491152311703, 0, 0.024317084074161062, 0])
    observed = lanczos_kernel(x, order=3)
    print(repr(expected), repr(observed))
    assert_allclose(expected, observed, atol=1e-9)
##
def test_lanczos_scalar():
    samples = np.zeros(20)
    x = 0
    order = 1
    expected = np.zeros_like(x)
    observed = lanczos_interpolate(x, samples, order)
    assert_array_almost_equal_nulp(expected, observed)

def test_lanczos_zero():
    samples = np.zeros(20)
    x = np.arange(-10, 10+1)
    order = 1
    expected = np.zeros_like(x)
    observed = lanczos_interpolate(x, samples, order)
    assert_array_almost_equal_nulp(expected, observed)

def test_lanczos_one():
    samples = np.ones(20)
    x = np.arange(-10, 10+1)
    order = 5
    expected = np.ones_like(x)
    observed = lanczos_interpolate(x, samples, order)
    print(expected, observed)
    assert_array_almost_equal_nulp(expected, observed)