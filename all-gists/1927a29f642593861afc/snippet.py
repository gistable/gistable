#!/usr/bin/env python
import numpy as np
import scipy.spatial.distance

if __name__ == '__main__':
    x = np.array([1, 1, 1, 1, 1])
    y = np.array([1, 0, 1, 0, 1])
    z = np.array([0, 1, 0, 0, 0])

    print 1 - scipy.spatial.distance.cosine(x, y)
    print 1 - scipy.spatial.distance.cosine(y, z)
    print 1 - scipy.spatial.distance.cosine(z, x)