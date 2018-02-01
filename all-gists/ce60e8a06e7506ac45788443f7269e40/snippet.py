""" A function that can read MNIST's idx file format into numpy arrays.

    The MNIST data files can be downloaded from here:
    
    http://yann.lecun.com/exdb/mnist/

    This relies on the fact that the MNIST dataset consistently uses
    unsigned char types with their data segments.
"""

import struct

import numpy as np

def read_idx(filename):
    with open(filename, 'rb') as f:
        zero, data_type, dims = struct.unpack('>HBB', f.read(4))
        shape = tuple(struct.unpack('>I', f.read(4))[0] for d in range(dims))
        return np.fromstring(f.read(), dtype=np.uint8).reshape(shape)