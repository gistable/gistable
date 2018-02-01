from __future__ import print_function

import multiprocessing
import ctypes
import numpy as np

def shared_array(shape):
    """
    Form a shared memory numpy array.
    
    http://stackoverflow.com/questions/5549190/is-shared-readonly-data-copied-to-different-processes-for-python-multiprocessing 
    """
    
    shared_array_base = multiprocessing.Array(ctypes.c_double, shape[0]*shape[1])
    shared_array = np.ctypeslib.as_array(shared_array_base.get_obj())
    shared_array = shared_array.reshape(*shape)
    return shared_array


# Form a shared array and a lock, to protect access to shared memory.
array = shared_array((1000, 1000))
lock = multiprocessing.Lock()


def parallel_function(i, def_param=(lock, array)):
    """
    Function that operates on shared memory.
    """
    
    # Make sure your not modifying data when someone else is.
    lock.acquire()    
    
    array[i, :] = i
    
    # Always release the lock!
    lock.release()

if __name__ == '__main__':
    """
    The processing pool needs to be instantiated in the main 
    thread of execution. 
    """
        
    pool = multiprocessing.Pool(processes=4)
        
    # Call the parallel function with different inputs.
    args = [(0), 
            (1), 
            (2)]
    
    # Use map - blocks until all processes are done.
    pool.map(parallel_function, args )
    
    print(array)