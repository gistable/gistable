import numpy as np, numpy.linalg as linalg
def fast_svd(M, k):
    p = k+5
    Y = np.dot(M, np.random.normal(size=(M.shape[1],p)))
    Q,r = linalg.qr(Y)
    B = np.dot(Q.T,M)
    Uhat, s, v = linalg.svd(B, full_matrices=False)
    U = np.dot(Q, Uhat)
    return U.T[:k].T, s[:k], v[:k]
