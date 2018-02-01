#!/usr/bin/env python
import numpy
from numpy.distutils.system_info import get_info
import sys
import timeit

print("version: %s" % numpy.__version__)
print("maxint:  %i\n" % sys.maxsize)

info = get_info('blas_opt')
print('BLAS info:')
for kk, vv in info.items():
    print(' * ' + kk + ' ' + str(vv))

setup = "import numpy; x = numpy.random.random((1000, 1000))"
count = 10

t = timeit.Timer("numpy.dot(x, x.T)", setup=setup)
print("\ndot: %f sec" % (t.timeit(count) / count))