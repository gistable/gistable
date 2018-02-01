import time

def timeit(f):

    def timed(*args, **kwargs):
        start = time.clock()
        for _ in range(100):
            f(*args, **kwargs)
        end = time.clock()
        return end - start
    return timed

@timeit
def append_loop(n):
    """Simple loop with append"""
    my_list = []
    for i in xrange(n):
        my_list.append(0)

@timeit
def add_loop(n):
    """Simple loop with +="""
    my_list = []
    for i in xrange(n):
        my_list += [0]

@timeit   
def list_comprehension(n):        
    """List comprehension"""
    my_list = [0 for i in xrange(n)]

@timeit
def integer_multiplication(n):
    """List and integer multiplication"""
    my_list = [0] * n


import numpy as np

@timeit
def numpy_array(n):
    my_list = np.zeros(n)
    

import pandas as pd 

df = pd.DataFrame([(integer_multiplication(n), numpy_array(n)) for n in range(1000)], 
                  columns=['Integer multiplication', 'Numpy array'])
df.plot()