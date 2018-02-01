import numpy as np
import numba as nb

from numba import types
from numba.extending import overload_method


@overload_method(types.Array, 'take')
def array_take(arr, indices):
   if isinstance(indices, types.Array):
       def take_impl(arr, indices):
           n = indices.shape[0]
           res = np.empty(n, arr.dtype)
           for i in range(n):
               res[i] = arr[indices[i]]
           return res
       return take_impl


@nb.jit(nopython=True)
def roll(a, shift):
    
    n = a.size
    reshape = True
    
    if n == 0:
        return a
    shift %= n
    
    indexes = np.concatenate((np.arange(n - shift, n), np.arange(n - shift)))
    
    res = a.take(indexes)
    if reshape:
        res = res.reshape(a.shape)
    return res


if __name__ == '__main__':
    a = np.arange(10)
    print np.allclose(np.roll(a, -2), roll(a, -2))
