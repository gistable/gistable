# -*- coding: utf-8 -*-
"""
http://www.cs.technion.ac.il/~ronrubin/Publications/KSVD-OMP-v2.pdf

parametrization by error is still in progress
"""
from time import time
import numpy as np
from scipy import linalg
import matplotlib.pyplot as pl

def unsparse(v, idx, length):
    """Transform a vector-index pair to a dense representation"""
    x = np.zeros(length)
    x[idx] = v
    return x

def orthogonal_mp(D, x, m, eps=None):
    """Orthogonal matching pursuit (OMP)
    
    Solves [1] min || D * gamma - x ||_2 subject to || gamma ||_0 <= m
    or     [2] min || gamma ||_0         subject to || D * gamma - x || <= eps
    
    Parameters
    ----------
        D, array of shape n_features x n_components
        x, vector of length n_features
        m, integer <= n_features
        eps, float (supersedes m)
        
    """
    residual = x
    idx = []
    if eps == None:
        stopping_condition = lambda: len(idx) == m
    else:
        stopping_condition = lambda: np.inner(residual, residual) <= eps

    while not stopping_condition():
        lam = np.abs(np.dot(residual, D)).argmax()
        idx.append(lam)
        gamma, _, _, _ = linalg.lstsq(D[:, idx], x)
        residual = x - np.dot(D[:, idx], gamma)
    return gamma, idx

def cholesky_omp(D, x, m, eps=None):
    if eps == None:
        stopping_condition = lambda: it == m  # len(idx) == m
    else:
        stopping_condition = lambda: np.inner(residual, residual) <= eps

    alpha = np.dot(x, D)
    
    #first step:        
    it = 1
    lam = np.abs(np.dot(x, D)).argmax()
    idx = [lam]
    L = np.ones((1,1))
    gamma = linalg.lstsq(D[:, idx], x)[0]
    residual = x - np.dot(D[:, idx], gamma)
    
    while not stopping_condition():
        lam = np.abs(np.dot(residual, D)).argmax()
        w = linalg.solve_triangular(L, np.dot(D[:, idx].T, D[:, lam]),
                                    lower=True, unit_diagonal=True)
        # should the diagonal be unit in theory? It crashes without it
        L = np.r_[np.c_[L, np.zeros(len(L))],
                  np.atleast_2d(np.append(w, np.sqrt(1 - np.dot(w.T, w))))]
        idx.append(lam)
        it += 1
        #gamma = linalg.solve(np.dot(L, L.T), alpha[idx], sym_pos=True)
        # what am I, stupid??
        Ltc = linalg.solve_triangular(L, alpha[idx], lower=True)
        gamma = linalg.solve_triangular(L, Ltc, trans=1, lower=True)
        residual = x - np.dot(D[:, idx], gamma)

    return gamma, idx

def _batch_omp_step(G, alpha_0, m, eps_0=None, eps=None):
    idx = []
    L = np.ones((1, 1))
    alpha = alpha_0
    eps_curr = eps_0
    delta = 0
    it = 0
    if eps == None:
        stopping_condition = lambda: it == m
    else:
        stopping_condition = lambda: eps_curr <= eps

    while not stopping_condition():
        lam = np.abs(alpha).argmax()
        if len(idx) > 0:
            w = linalg.solve_triangular(L, G[idx, lam],
                                        lower=True,  unit_diagonal=True)
            L = np.r_[np.c_[L, np.zeros(len(L))],
                      np.atleast_2d(np.append(w, np.sqrt(1 - np.inner(w, w))))]
        idx.append(lam)
        it += 1
        Ltc = linalg.solve_triangular(L, alpha_0[idx], lower=True)
        gamma = linalg.solve_triangular(L, Ltc, trans=1, lower=True) 
        beta = np.dot(G[:, idx], gamma)        
        alpha = alpha_0 - beta
        if eps != None:
            eps_curr += delta
            delta = np.inner(gamma, beta[idx])
            eps_curr -= delta
    return gamma, idx                 

def batch_omp(D, X, m, eps=None):
    """Precomputations for batch OMP"""
    Alpha = np.dot(D.T, X)
#    Eps = np.dot(X.T, X) sh**!
    G = np.dot(D.T, D)
    func = lambda a: unsparse(*_batch_omp_step(G, a, m), length=D.shape[1])
    V = np.apply_along_axis(func, axis=0, arr=Alpha)
    return V

def generate_dict(n_features, n_components):
    # generate random dictionary
    D = np.random.randn(n_components, n_features)
    D /= np.apply_along_axis(lambda x: np.sqrt(np.dot(x.T, x)), 0, D)
    return D
    
def generate_data(D, sparsity):
    n_features = D.shape[1]
    # generate sparse signal
    x = np.zeros(n_features)
    indices = np.random.randint(0, n_features, sparsity)
    x[indices] = np.random.normal(0, 5, sparsity)
    return (indices, x), np.dot(D, x)

def bench_plot():    
    np.random.seed(42)
    n_features, n_components = 512, 1024
    print "generating dictionary..."
    D = generate_dict(n_features, n_components)
    sparsities = np.arange(50, 200, 15)
    print "generating signals..."
    Y = np.zeros((n_components, len(sparsities)))
    X = np.zeros((n_features, len(sparsities)))    
    for i, sp in enumerate(sparsities):
        (_, X[:, i]), Y[:, i] = generate_data(D, sp)
    print "precomputing..."
    G = np.dot(D.T, D)
    A = np.dot(D.T, Y)
    naive, cholesky, batch = [], [], []
    naive_err, cholesky_err, batch_err = [], [], []
    for i in xrange(len(sparsities)):
        print "sparsity: ", sparsities[i]
        t0 = time()
        x, idx = orthogonal_mp(D, Y[:, i], sparsities[i])
        naive.append(time() - t0)
        naive_err.append(linalg.norm(X[:, i] - unsparse(x, idx, n_features)))
        t0 = time()
        x, idx = cholesky_omp(D, Y[:, i], sparsities[i])
        cholesky.append(time() - t0)        
        cholesky_err.append(linalg.norm(X[:, i] - unsparse(x, idx, n_features)))
        t0 = time()
        x, idx = _batch_omp_step(G, A[:, i], sparsities[i])
        batch.append(time() - t0)        
        batch_err.append(linalg.norm(X[:, i] - unsparse(x, idx, n_features)))
    pl.figure()
    pl.subplot(1, 2, 1)
    pl.xlabel('Sparsity level')
    pl.ylabel('Time')
    pl.plot(sparsities, naive, 'o-', label="Naive implementation")
    pl.plot(sparsities, cholesky, 'o-', label="Cholesky update OMP")
    pl.plot(sparsities, batch, 'o-', label="Batch OMP")
    pl.legend()
    pl.subplot(1, 2, 2)
    pl.xlabel('Sparsity level')
    pl.ylabel('Error')   
    pl.plot(sparsities, naive_err, 'o-', label="Naive implementation")
    pl.plot(sparsities, batch_err, 'o-', label="Batch OMP")
    pl.plot(sparsities, cholesky_err, 'o-', label="Cholesky update OMP")
    pl.legend()
    
    pl.show()    

def plot_reconstruction():
    # init
    np.random.seed(42)
    D = generate_dict(n_features=512, n_components=100)
    sparsity = 17
    (indices, x), y = generate_data(D, sparsity)
    pl.subplot(3, 1, 1)
    pl.title("Sparse signal")
    pl.stem(indices, x[indices])
    y_noise = y + np.random.normal(0, 0.05, y.shape)
    
    #x_r, i_r = cholesky_omp(D, y, sparsity)
    x_r, i_r = _batch_omp_step(np.dot(D.T, D), np.dot(D.T,y), sparsity)
    pl.subplot(3, 1, 2)
    pl.title("Recovered signal from noise-free measurements")    
    pl.stem(i_r, x_r)
    
    #x_r, i_r = cholesky_omp(D, y_noise, sparsity)
    x_r, i_r = _batch_omp_step(np.dot(D.T, D), np.dot(D.T,y_noise), sparsity)
    pl.subplot(3, 1, 3)
    pl.title("Recovered signal from noisy measurements")    
    pl.stem(i_r, x_r)
    pl.show()
    
if __name__ == '__main__':    
    bench_plot()
    plot_reconstruction()

