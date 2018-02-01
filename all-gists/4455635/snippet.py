import numpy as np

def fast_hist(data, bin_edges):
    """Fast 1-dimensional histogram. Comparable to numpy.histogram(), but careless.
    
    'bin_edges' should encompass all values in 'data'; the first and last elements 
    in 'bin_edges' are ignored, and are effectively (-infinity, infinity).

    Returns the histogram array only.
    """
    # Yes, I've tested this against histogram().
    return np.bincount(np.digitize(data, bin_edges[1:-1]), minlength=len(bin_edges) - 1)
def fast_hist_2d(data, bin_edges):
    """Fast 2-dimensional histogram. Comparable to numpy.histogramdd(), but careless.
    
    'data' is an Nx2 array. 'bin_edges' is used for both dimensions and should
    encompass all values in 'data'; the first and last elements in 'bin_edges'
    are ignored, and are effectively (-infinity, infinity).

    Returns the histogram array only.
    """
    # Yes, I've tested this against histogramdd().
    xassign = np.digitize(data[:,0], bin_edges[1:-1]) 
    yassign = np.digitize(data[:,1], bin_edges[1:-1])
    nbins = len(bin_edges) - 1
    flatcount = np.bincount(xassign + yassign * nbins, minlength=nbins*nbins)
    return flatcount.reshape((nbins, nbins)).T