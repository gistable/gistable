#!/usr/bin/env python2.7

import scipy.ndimage as ndimage
import numpy

def local_maxima(array, min_distance = 1, periodic=False, edges_allowed=True): 
    """Find all local maxima of the array, separated by at least min_distance."""
    array = numpy.asarray(array)
    cval = 0 
    if periodic: 
        mode = 'wrap' 
    elif edges_allowed: 
        mode = 'nearest' 
    else: 
        mode = 'constant' 
    cval = array.max()+1 
    max_points = array == ndimage.maximum_filter(array, 1+2*min_distance, mode=mode, cval=cval) 
    return [indices[max_points] for indices in numpy.indices(array.shape)]

s = [1, 4, 6, 8, 3, 2, 0]
d = [2, 4, 6, 8, 23, 6, 4, 2, 5, 7, 8, 9, 4, 2, 0]

print local_maxima(s)
print local_maxima(d)
