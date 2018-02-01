from itertools import count
from collections import defaultdict
import numpy as np
from scipy.sparse import csr
    
def vectorize(lil, ix=None, p=None):
    """ 
    Creates a scipy csr matrix from a list of lists (each inner list is a set of values corresponding to a feature) 
    
    parameters:
    -----------
    lil -- list of lists (dimension of inner lists should be the same)
    ix -- index generator (default None)
    p -- dimension of featrure space (number of columns in the sparse matrix) (default None)
    """
    if (ix == None):
        ix = defaultdict(count(0).next)
    
    n = len(lil[0]) # num samples
    g = len(lil) # num groups
    nz = n * g # number of non-zeros

    col_ix = np.empty(nz, dtype=int)
    
    for i, d in enumerate(lil):
        # append index k with __i in order to prevet mapping different columns with same id to same index
        col_ix[i::g] = [ix[str(k) + '__' + str(i)] for k in d]

    row_ix = np.repeat(np.arange(0, n), g)
    data = np.ones(nz)
    
    if (p == None):
        p = len(ix)
    
    # only features that are less than p (siz of feature vector) are considered
    ixx = np.where(col_ix < p)
    
    return csr.csr_matrix((data[ixx], (row_ix[ixx], col_ix[ixx])), shape=(n, p)), ix