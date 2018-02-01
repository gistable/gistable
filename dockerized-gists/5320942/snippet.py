from timeit import Timer
import numpy as np
import math

def timer(*funcs):
    # find the maximum function name length
    if len(funcs) > 1:
        maxlen = max(*[len(func) for func in funcs])
    elif len(funcs) == 1:
        maxlen = len(funcs[0])
    else:
        return

    # run each function 10000 times and print statistics
    times = []
    print "--"
    for func in funcs:
        timerfunc = Timer("%s()" % func, "from __main__ import %s" % func)
        runtime = timerfunc.repeat(repeat=10000, number=1)
        mtime = np.mean(runtime)
        stime = np.std(runtime)
        dfunc = func + (" " * (maxlen - len(func) + 1))
        print "%s: %.6f +/- %.6f seconds" % (dfunc, mtime, stime)
        times.append(runtime)
    return times

######################################################################
# Ranges

def numpy_arange():
    l = np.arange(1000)
def py_range():
    l = range(1000)
def py_xrange():
    l = xrange(1000)

timer("numpy_arange", "py_range", "py_xrange")

def py_xrange_list():
    l = list(xrange(1000))

timer("py_xrange_list")

def arange_to_list():
    l = list(np.arange(1000))
def xrange_to_ndarray():
    l = np.array(xrange(1000))
def range_to_ndarray():
    l = np.array(range(1000))

timer("arange_to_list", "xrange_to_ndarray", "range_to_ndarray")

######################################################################
# Sum a list of integers

def numpy_sum():
    total = np.sum(np.arange(1000))
def loop_sum():
    total = 0
    for i in xrange(1000):
        total += i

timer("numpy_sum", "loop_sum")

######################################################################
# Compute the mean and standard deviation of a list of numbers

def numpy_mean():
    mean = np.mean(np.arange(1000))
def loop_mean():
    def _mean(arr):
        # sum all the numbers
        total = 0
        for num in arr:
            total += num
        # calculate the mean
        mean = total / float(len(arr))
        return mean
    mean = _mean(range(1000))

def numpy_std():
    std = np.std(np.arange(1000))
def loop_std():
    def _std(arr):
        # calculate the mean
        total = 0
        for num in arr:
            total += num
        mean = total / float(len(arr))
        # calculate the variance
        total = 0
        for num in arr:
            total += (num - mean) ** 2
        var = total / float(len(arr))
        # standard deviation is square root of the variance
        std = math.sqrt(var)
        return std
    std = _std(range(1000))

timer("numpy_mean", "loop_mean", "numpy_std", "loop_std")

######################################################################
# Make a list of the first 10000 squares

def numpy_squares():
    squares = np.arange(1, 10001) ** 2
def listcomp_squares():
    squares = [i**2 for i in xrange(1, 10001)]
def loop_squares():
    squares = []
    for i in xrange(1, 10001):
        squares.append(i ** 2)

timer("numpy_squares", "listcomp_squares", "loop_squares")

######################################################################
# Make a grid out of an arbitrary number of (numerical) 1D
# lists/arrays

def numpy_make_grid(*args):
    # an array of ones in the overall shape, for broadcasting
    ones = np.ones([len(arg) for arg in args])
    # mesh grids of the index arrays
    midx = [(ix * ones)[None] for ix in np.ix_(*args)]
    # make into one Nx3 array
    idx = np.concatenate(midx).reshape((len(args), -1)).transpose()
    return idx

def loop_make_grid(*args):
    # find the sizes of each dimension and the total size of the
    # final array
    shape = [len(arg) for arg in args]
    size = 1
    for sh in shape:
        size *= sh
    # make a list of lists to hold the indices
    l = [1 for i in xrange(len(args))]
    idx = [l[:] for i in xrange(size)]
    # fill in the indices
    rep = 1
    for aidx, arg in enumerate(args):
        # repeat each value in the dimension based on which
        # dimensions we've already included
        vals = []
        for val in arg:
            vals.extend([val] * rep)
        # repeat each dimension based on which dimensions we
        # haven't already included and actually fill in the
        # indices
        rest = size / (rep * len(arg))
        for vidx, val in enumerate(vals * rest):
            idx[vidx][aidx] = val
        rep *= len(arg)
    return idx

def numpy_indices():
    numpy_make_grid(np.arange(10), np.arange(10), np.arange(10))
def loop_indices():
    loop_make_grid(range(10), range(10), range(10))

timer("numpy_indices", "loop_indices")