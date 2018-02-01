import numpy as np

def array_for_sliding_window(x, wshape):
    """Build a sliding-window representation of x.

    The last dimension(s) of the output array contain the data of
    the specific window.  The number of dimensions in the output is 
    twice that of the input.

    Parameters
    ----------
    x : ndarray_like
       An array for which is desired a representation to which sliding-windows 
       computations can be easily applied.
    wshape : int or tuple
       If an integer, then it is converted into a tuple of size given by the 
       number of dimensions of x with every element set to that integer.
       If a tuple, then it should be the shape of the desired window-function

    Returns
    -------
    out : ndarray
        Return a zero-copy view of the data in x so that operations can be 
        performed over the last dimensions of this new array and be equivalent 
        to a sliding window calculation.  The shape of out is 2*x.ndim with 
        the shape of the last nd dimensions equal to wshape while the shape 
        of the first n dimensions is found by subtracting the window shape
        from the input shape and adding one in each dimension.  This is 
        the number of "complete" blocks of shape wshape in x.

    Raises
    ------
    ValueError
        If the size of wshape is not x.ndim (unless wshape is an integer).
        If one of the dimensions of wshape exceeds the input array. 

    Examples
    --------
    >>> x = np.linspace(1,5,5)
    >>> x
    array([ 1.,  2.,  3.,  4.,  5.])

    >>> array_for_rolling_window(x, 3)
    array([[ 1.,  2.,  3.],
           [ 2.,  3.,  4.],
           [ 3.,  4.,  5.]])
           
    >>> x = np.arange(1,17).reshape(4,4)
    >>> x
    array([[ 1,  2,  3,  4],
           [ 5,  6,  7,  8],
           [ 9, 10, 11, 12],
           [13, 14, 15, 16]])

    >>> array_for_rolling_window(x, 3)
    array([[[[ 1,  2,  3],
             [ 5,  6,  7],
             [ 9, 10, 11]],

            [[ 2,  3,  4],
             [ 6,  7,  8],
             [10, 11, 12]]],

           [[[ 5,  6,  7],
             [ 9, 10, 11],
             [13, 14, 15]],

            [[ 6,  7,  8],
             [10, 11, 12],
             [14, 15, 16]]]])
    """
    x = np.asarray(x)

    try:
        nd = len(wshape)
    except TypeError:
        wshape = tuple(wshape for i in x.shape)
        nd = len(wshape)
    if nd != x.ndim:
        raise ValueError("wshape has length {0} instead of "
                         "x.ndim which is {1}".format(len(wshape), x.ndim)) 
    
    out_shape = tuple(xi-wi+1 for xi, wi in zip(x.shape, wshape)) + wshape
    if not all(i>0 for i in out_shape):
        raise ValueError("wshape is bigger than input array along at "
                         "least one dimension")

    out_strides = x.strides*2
    
    return np.lib.stride_tricks.as_strided(x, out_shape, out_strides)
