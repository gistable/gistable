#!/opt/local/bin/python
# module power iteration clustering

import numpy as NP
from scipy.cluster.vq import kmeans2

def calcNorm1(v):
    return NP.sum(NP.fabs(v))

def calcDelta(v,v2):
    return NP.sum(NP.fabs(v2-v))

def normalize(v):
    max=v.max()
    min=v.min()
    return (v-min)/(max-min)

def initVector(m):
    n=m.shape[0]
    ovec=NP.matrix(NP.ones(n)).T
    v=m*ovec
    sinv=1.0/NP.sum(v)
    return v*sinv

def pic(a,maxiter,eps):
    m=NP.matrix(a)
    d1=NP.matrix(NP.diag(a.sum(0))).I
    w=d1*m
    n=w.shape[0]
    #v=NP.matrix(NP.random.random(n)).T#一様乱数で初期化
    v=initVector(m)#論文にある初期化手法を用いる
    for i in range(maxiter):
        v2=w*v
        ninv=1.0/calcNorm1(v2)
        v2*=ninv
        delta=calcDelta(v,v2)
        v=v2
        if (delta*n)<eps:
            break
    return normalize(v)

if __name__ == '__main__':
    matrix=NP.array([[10.0000, 0.7071, 0.3333, 0.2774, 0.3714],
                  [0.7071, 10.0000, 0.4472, 0.2774, 0.2857],
                 [0.3333, 0.4472, 10.0000, 0.5000, 0.3124],
                  [0.2774, 0.2774, 0.5000, 10.0000, 0.4851],
                 [0.3714, 0.2857, 0.3124, 0.4851, 10.0000]])
    v=pic(matrix,10000,1.0e-5)
    print kmeans2(v,2)
