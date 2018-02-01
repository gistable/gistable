#!/usr/bin/env python

"""
This is a super dumb script to test pytables write speeds/compression ratios
for various algorithms and various data sparsities.

TJL Feb 2014
"""

import os
import tables
import time
import numpy as np

DATA_TYPE = np.float64
TARGET = '.'
ARRAY_SHAPE = (1000, 10000)

def test_compression(density, algorithm, complevel=1):

    compression = tables.Filters(complib=algorithm, shuffle=True, complevel=complevel)
    filename = os.path.join(TARGET, 'tmptest.h5')

    data = np.random.binomial(1, density, size=(1, ARRAY_SHAPE[0], ARRAY_SHAPE[1]))
    #print 'Sparsity:', (np.sum((data == 0.0)) / float(x*y))

    f = tables.File(filename, 'w')
    a = tables.Atom.from_dtype(np.dtype(np.float64))
    pi_node = f.createEArray(where='/', name='data',
                             shape=(0, ARRAY_SHAPE[0], ARRAY_SHAPE[1]), 
                             atom=a, filters=compression)
                             
    start = time.time()
    pi_node.append(data)
    f.close()
    end = time.time()
    
    time_elapsed = end - start
    
    st = os.stat(filename)
    du = st.st_size #st.st_blocks * st.st_blksize
    
    os.remove(filename)
    
    return float(du), time_elapsed
    
    
def test_algorithm(algorithm, density=0.1):
    
    du0, time0 = test_compression(density, algorithm, complevel=0)
    du1, time1 = test_compression(density, algorithm, complevel=1)
    
    print '%s\t%.2f\t%.4f\t\t%f' % (algorithm, density, du1/du0, (du0 / 1.e6) / time1)
    
    return
    
    
def main():
    
    print ''
    print 'TESTING SPARSE COMPRESSION ALGORITHMS'
    print 'HDF5 =            %s' % tables.hdf5Version
    print 'PYTABLES =        %s' % tables.__version__
    print 'DATA TYPE =       %s' % str(DATA_TYPE)
    print 'ARRAY SIZE =      %s' % str(ARRAY_SHAPE)
    print 'TARGET ON DISK =  %s' % TARGET
    
    
    densities = [1.0, 0.75, 0.5, 0.25, 0.01]
    print ''
    print 'Algo\tDensity\tCompr Ratio\tWrite Speed (MB/s)'
    print '----\t-------\t-----------\t------------------'
    [test_algorithm('zlib', x) for x in densities]
    [test_algorithm('blosc', x) for x in densities]
    
    return
    
    
if __name__ == '__main__':
    main()
