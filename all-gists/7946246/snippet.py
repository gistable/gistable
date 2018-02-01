import numpy as np
import numpy
import theano
import theano.tensor as T
from theano import function, config, shared, sandbox
from theano import ProfileMode
from sklearn import cluster, datasets
import matplotlib.pyplot as plt

def rsom(data, cluster_num, alpha, epochs = -1, batch = 1, verbose = False):   
    rng = np.random
    
    # From Kohonen's paper
    if epochs == -1:
        print data.shape[0]
        epochs = 500 * data.shape[0]
    
    # Symmbol variables
    X = T.dmatrix('X')
    WIN = T.dmatrix('WIN')
    
    # Init weights random
    W = theano.shared(rng.randn(cluster_num, data.shape[1]), name="W")
    W_old = W.get_value()
    
    # Find winner unit
    bmu = ((W**2).sum(axis=1, keepdims=True) + (X**2).sum(axis=1, keepdims=True).T - 2*T.dot(W, X.T)).argmin(axis=0)
    dist = T.dot(WIN.T, X) - WIN.sum(0)[:, None] * W
    err = abs(dist).sum()
    
    update = function([X,WIN],outputs=err,updates=[(W, W + alpha * dist)], mode="FAST_RUN")
    find_bmu = function([X], bmu, mode="FAST_RUN")
    
    if any([x.op.__class__.__name__ in ['Gemv', 'CGemv', 'Gemm', 'CGemm'] for x in
            update.maker.fgraph.toposort()]):
        print 'Used the cpu'
    elif any([x.op.__class__.__name__ in ['GpuGemm', 'GpuGemv'] for x in
            update.maker.fgraph.toposort()]):
        print 'Used the gpu'
    else:
        print 'ERROR, not able to tell if theano used the cpu or the gpu'
        print update.maker.fgraph.toposort()
    
    
    # Update
    for epoch in range(epochs):
        C = 0
        for i in range(0, data.shape[0], batch):
            D = find_bmu(data[i:i+batch, :])
            S = np.zeros([batch,cluster_num])
            S[range(batch),D] = 1
            cost = update(data[i:i+batch, :], S)
            
        if epoch%10 == 0 and verbose:
            print "Avg. centroid distance -- ", cost.sum(),"\t EPOCH : ", epoch
    return W.get_value()

def kmeans(X, cluster_num, numepochs, learningrate=0.01, batchsize=100, verbose=True): 
    rng = numpy.random
    W =rng.randn(cluster_num, X.shape[1])
    X2 = (X**2).sum(1)[:, None]
    for epoch in range(numepochs):
        for i in range(0, X.shape[0], batchsize):
            D = -2*numpy.dot(W, X[i:i+batchsize,:].T) + (W**2).sum(1)[:, None] + X2[i:i+batchsize].T
            S = (D==D.min(0)[None,:]).astype("float").T
            W += learningrate * (numpy.dot(S.T, X[i:i+batchsize,:]) - S.sum(0)[:, None] * W) 
        if verbose:
            print "epoch", epoch, "of", numepochs, " cost: ", D.min(0).sum()
    return W


# Test Codes
blobs = datasets.make_blobs(n_samples=4000, random_state=8)
noisy_moons = datasets.make_moons(n_samples=4000, noise=.05)
noisy_circles = datasets.make_circles(n_samples=2000, factor=.5,
                                      noise=.05)

DATA = noisy_circles[0]

import time
t1 = time.time()
W = rsom(DATA ,3,alpha = 0.001, epochs=100, batch=10, verbose=True)
t2 = time.time()

t3 = time.time()
W2 = kmeans(DATA, 3, numepochs = 100, batchsize=10, learningrate=0.001)
t4 = time.time()

print "RSOM : ",t2-t1
print "kmeans : ", t4-t3

plt.scatter(DATA[:,0], DATA[:,1], color='red')
plt.scatter(W[:,0],W[:,1],color='blue',s=20,edgecolor='none')
plt.scatter(W2[:,0],W2[:,1],color='yellow',s=20,edgecolor='none')