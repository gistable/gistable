"""http://stackoverflow.com/questions/6282432/load-sparse-array-from-npy-file
"""
import random
import scipy.sparse as sparse
import scipy.io
import numpy as np

def save_sparse_matrix(filename, x):
    x_coo = x.tocoo()
    row = x_coo.row
    col = x_coo.col
    data = x_coo.data
    shape = x_coo.shape
    np.savez(filename, row=row, col=col, data=data, shape=shape)

def load_sparse_matrix(filename):
    y = np.load(filename)
    z = sparse.coo_matrix((y['data'], (y['row'], y['col'])), shape=y['shape'])
    return z

N=20000
x = sparse.lil_matrix( (N,N) )
for i in xrange(N):
    x[random.randint(0,N-1),random.randint(0,N-1)]=random.randint(1,100)

save_sparse_matrix('/tmp/my_array',x)
load_sparse_matrix('/tmp/my_array.npz').tolil()