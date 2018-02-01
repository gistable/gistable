#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
正準相関分析
cca.py
'''

import numpy as np
import scipy as sp
from scipy import linalg as LA
from scipy.spatial import distance as DIST


def cca(X, Y):
    '''
    正準相関分析
    http://en.wikipedia.org/wiki/Canonical_correlation
    '''    
    n, p = X.shape
    n, q = Y.shape

    # zero mean
    X = X - X.mean(axis=0)
    Y = Y - Y.mean(axis=0)

    # covariances
    S = np.cov(X.T, Y.T, bias=1)

    # S = np.corrcoef(X.T, Y.T)
    SXX = S[:p,:p]
    SYY = S[p:,p:]
    SXY = S[:p,p:]
    SYX = S[p:,:p]

    # 
    sqx = LA.sqrtm(LA.inv(SXX)) # SXX^(-1/2)
    sqy = LA.sqrtm(LA.inv(SYY)) # SYY^(-1/2)
    M = np.dot(np.dot(sqx, SXY), sqy.T) # SXX^(-1/2) * SXY * SYY^(-T/2)
    A, s, Bh = LA.svd(M, full_matrices=False)
    B = Bh.T

    U = np.dot(np.dot(A.T, sqx), X.T).T
    V = np.dot(np.dot(B.T, sqy), Y.T).T

    return s, A, B, U, V


def gaussian_kernel(x, y, var=1.0):
    return np.exp(-np.linalg.norm(x - y) ** 2 / (2 * var))

def polynomial_kernel(x, y, c=1.0, d=2.0):
    return (np.dot(x, y) + c) ** d

def kcca(X, Y, kernel_x=gaussian_kernel, kernel_y=gaussian_kernel, eta=1.0):
    '''
    カーネル正準相関分析
    http://staff.aist.go.jp/s.akaho/papers/ibis00.pdf
    '''
    n, p = X.shape
    n, q = Y.shape

    Kx = DIST.squareform(DIST.pdist(X, kernel_x))
    Ky = DIST.squareform(DIST.pdist(Y, kernel_y))
    J = np.eye(n) - np.ones((n, n)) / n
    M = np.dot(np.dot(Kx.T, J), Ky) / n
    L = np.dot(np.dot(Kx.T, J), Kx) / n + eta * Kx
    N = np.dot(np.dot(Ky.T, J), Ky) / n + eta * Ky

    sqx = LA.sqrtm(LA.inv(L))
    sqy = LA.sqrtm(LA.inv(N))

    a = np.dot(np.dot(sqx, M), sqy.T)
    A, s, Bh = LA.svd(a, full_matrices=False)
    B = Bh.T

    # U = np.dot(np.dot(A.T, sqx), X).T
    # V = np.dot(np.dot(B.T, sqy), Y).T

    return s, A, B


def get_data_1():
    X = np.array([[2,1],[1,2],[0,0],[-1,-2],[-2,-1]])
    Y = np.array([[2,2],[-1,-1],[0,0],[-2,1],[1,-2]])
    return X, Y

def get_data_2():
    n = 100
    theta = (np.random.rand(n) - 0.5) * np.pi
    x1 = np.sin(theta)
    x2 = np.sin(3 * theta)
    X = np.vstack([x1, x2]).T + np.random.randn(n, 2) * .05
    y1 = np.exp(theta) * np.cos(2 * theta)
    y2 = np.exp(theta) * np.sin(2 * theta)
    Y = np.vstack([y1, y2]).T + np.random.randn(n, 2) * .05
    return X, Y

def test_cca():
    X, Y = get_data_1()
    cca(X, Y)
    X, Y = get_data_2()
    cca(X, Y)

def test_kcca():
    X, Y = get_data_1()
    kcca(X, Y)
    X, Y = get_data_2()
    kcca(X, Y)

if __name__ == '__main__':
    test_cca()
    test_kcca()