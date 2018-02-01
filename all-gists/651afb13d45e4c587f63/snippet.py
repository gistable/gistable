# -*- coding: utf-8 -*-
"""
Reproducing the results of Auto-Encoding Variational Bayes by Kingma and Welling
With a little help from the code from van Amersfoort and Otto Fabius (https://github.com/y0ast)

@author: Pedro Tabacof (tabacof at gmail dot com)
"""

import random
import numpy as np
from scipy.stats import norm
import time

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.gridspec as gridspec

# From Theano tutorial - MNIST dataset
from logistic_sgd import load_data

import theano
import theano.tensor as T

start_time = time.time()

n_latent = 10
n_hidden = 500
n_input = 28*28
# Right now the code only works with one expectation (like the article), but this can be easily fixed
n_expectations = 1 
batch_size = 100
n_epochs = 25000

random.seed(0)
np.random.seed(1)

# The functions below were adapted from the amazing Theano tutorial by Newmu
# https://github.com/Newmu/Theano-Tutorials

def floatX(X):
    return np.asarray(X, dtype=theano.config.floatX)

def init_weights(shape):
    return theano.shared(floatX(np.random.randn(*shape) * 0.01))

def sgd(cost, params, lr=0.05, momentum = 0.9):
    grads = T.grad(cost=cost, wrt=params)
    updates = []
    for p, g in zip(params, grads):
        acc = theano.shared(p.get_value() * 0.)
        acc_new =  acc*momentum + (1.0-momentum)*g
        updates.append([acc, acc_new])
        updates.append([p, p - acc_new * lr])
    return updates
    
def adagrad(cost, params, lr=0.001, epsilon=1e-6):
    grads = T.grad(cost=cost, wrt=params)
    updates = []
    for p, g in zip(params, grads):
        acc = theano.shared(p.get_value() * 0.)
        acc_new = acc + g ** 2
        gradient_scaling = T.sqrt(acc_new + epsilon)
        g = g / gradient_scaling
        updates.append((acc, acc_new))
        updates.append((p, p - lr * g))
    return updates
  
def RMSprop(cost, params, lr=0.001, rho=0.9, epsilon=1e-6):
    grads = T.grad(cost=cost, wrt=params)
    updates = []
    for p, g in zip(params, grads):
        acc = theano.shared(p.get_value() * 0.)
        acc_new = rho * acc + (1 - rho) * g ** 2
        gradient_scaling = T.sqrt(acc_new + epsilon)
        g = g / gradient_scaling
        updates.append((acc, acc_new))
        updates.append((p, p - lr * g))
    return updates
    
# Parameters
# Gaussian MLP weights and biases (encoder)
gaussian_bh = init_weights((n_hidden, ))
mu_bo = init_weights((n_latent, ))
sigma_bo = init_weights((n_latent, ))

gaussian_Wh = init_weights((n_input, n_hidden))
mu_Wo = init_weights((n_hidden, n_latent))
sigma_Wo = init_weights((n_hidden, n_latent))

# Bernoulli MLP weights and biases (decoder)
bernoulli_bh = init_weights((n_hidden, ))
bernoulli_bo = init_weights((n_input, ))

bernoulli_Wh = init_weights((n_latent, n_hidden))
bernoulli_Wo = init_weights((n_hidden, n_input))

# Only the weight matrices W will be regularized (weight decay)
W = [gaussian_Wh, mu_Wo, sigma_Wo, bernoulli_Wh, bernoulli_Wo]
b = [gaussian_bh, mu_bo, sigma_bo, bernoulli_bh, bernoulli_bo]
params = W + b

# Gaussian Encoder
x = T.matrix("x")
h_encoder = T.tanh(T.dot(x, gaussian_Wh) + gaussian_bh)
mu = T.dot(h_encoder, mu_Wo) + mu_bo
log_sigma = 0.5*(T.dot(h_encoder, sigma_Wo) + sigma_bo)
# This expression is simple (not an expectation) because we're using normal priors and posteriors
DKL = (1.0 + 2.0*log_sigma - mu**2 - T.exp(2.0*log_sigma)).sum(axis = 1)/2.0

# Bernoulli Decoder
std_normal = T.matrix("std_normal") 
z = mu + T.exp(log_sigma)*std_normal
h_decoder = T.tanh(T.dot(z, bernoulli_Wh) + bernoulli_bh)
y = T.nnet.sigmoid(T.dot(h_decoder, bernoulli_Wo) + bernoulli_bo)
log_likelihood = -T.nnet.binary_crossentropy(y, x).sum(axis = 1)

# Lower bound
lower_bound = -(DKL + log_likelihood).mean()
# Weight decay
L2 = sum([(w**2).sum() for w in W])
cost = lower_bound + batch_size/50000.0/2.0*L2

#updates = sgd(lower_bound, params, lr = 0.001)
updates = RMSprop(cost, params, lr=0.001)
#updates = adagrad(lower_bound, params, lr=0.02)

train_model = theano.function(inputs=[x, std_normal], 
                              outputs=cost, 
                              updates=updates,
                              mode='FAST_RUN',
                              allow_input_downcast=True)
                              
eval_model = theano.function(inputs=[x, std_normal], outputs=lower_bound,
                             mode='FAST_RUN',
                             allow_input_downcast=True) 

print("--- %s seconds ---" % (time.time() - start_time))
start_time = time.time()

# Load MNIST and binarize it
datasets = load_data('mnist.pkl.gz')
train_x, _ = datasets[0]
train_x = 1.0*(train_x > 0.5)
val_x, _ = datasets[1]
val_x = 1.0*(val_x > 0.5)
tx = theano.function([], T.concatenate([train_x, val_x]))()
# Using the test set as validation
tst_x, _ = datasets[2]
tst_x = 1.0*(tst_x > 0.5)
vx = theano.function([], tst_x)()

print("--- %s seconds ---" % (time.time() - start_time))
start_time = time.time()

training = []
validation = []
for i in range(n_epochs):
    minibatch_train = [ tx[j] for j in random.sample(xrange(len(tx)), batch_size) ]

    val_cost = eval_model(vx, np.random.normal(size = (len(vx), n_latent)))
    train_cost = train_model(minibatch_train, np.random.normal(size = (batch_size, n_latent)))
    
    print "epoch", i, "train", train_cost, "val", val_cost
    
    training.append(train_cost)
    validation.append(val_cost)    

plt.subplot(211)
plt.ylabel("-Lower bound")
plt.xlabel("Minibatch (" + str(batch_size) + " samples)")
plt.plot(training, label = "Train")
plt.legend()
plt.subplot(212)
plt.ylabel("-Lower bound")
plt.xlabel("Minibatch (" + str(batch_size) + " samples)")
plt.plot(validation, 'r', label = "Validation")
plt.legend()
plt.show()

print("--- %s seconds ---" % (time.time() - start_time))
start_time = time.time()

# Now let's test the auto-encoder on some visual problems

# "Deterministic" decoder (uses only the mean of the Gaussian encoder)
t = T.vector()
h_mu = T.tanh(T.dot(t, gaussian_Wh) + gaussian_bh)
h_bern = T.tanh(T.dot(T.dot(h_mu, mu_Wo) + mu_bo, bernoulli_Wh) + bernoulli_bh)
yt = T.nnet.sigmoid(T.dot(h_bern, bernoulli_Wo) + bernoulli_bo)
test_input = theano.function([t], yt,
                             mode='FAST_RUN',
                             allow_input_downcast=True)


# Reconstruct some random images (with optional salt and peper noise)
salt_pepper = 0.2

plt.figure()#figsize = (5, 2))
gs1 = gridspec.GridSpec(5, 2)
gs1.update(wspace=0.0, hspace=0.0) # set the spacing between axes. 

for i in range(5):
    test = vx[random.randint(0, len(vx))]
    test = np.array([test[j] if u > salt_pepper else np.random.choice([0, 1]) for u, j in zip(np.random.uniform(size = n_input), range(n_input))])
    plt.subplot(gs1[2*i])
    plt.axis('off')
    plt.imshow(test.reshape((28, 28)), cmap = cm.Greys_r)
    plt.subplot(gs1[2*i + 1])
    plt.axis('off')
    plt.imshow(test_input(test).reshape((28, 28)), cmap = cm.Greys_r)
plt.show()

# Now let's visualize the learned manifold
# We only need the decoder for this (and some way to generate latent variables)
t = T.vector()
h = T.tanh(T.dot(t, bernoulli_Wh) + bernoulli_bh)
yt = T.nnet.sigmoid(T.dot(h, bernoulli_Wo) + bernoulli_bo)
visualize = theano.function([t], yt,
                            mode='FAST_RUN',
                            allow_input_downcast=True)

# Size of visualizations
size = 10

# For 2 latent variables the manifold can be fully explored on a grid
plt.figure(figsize = (size, size))
gs1 = gridspec.GridSpec(size, size)
gs1.update(wspace=0.0, hspace=0.0) # set the spacing between axes. 

ppf = np.linspace(1E-3, 1.0 - 1E-3, size)
if n_latent == 2:
    for i in range(size):
        for j in range(size):
            plt.subplot(gs1[size*i + j])
            plt.axis('off')
            image = 1.0 - visualize([norm.ppf(ppf[i]), norm.ppf(ppf[j])])
            plt.imshow(image.reshape((28, 28)), cmap = cm.Greys_r)
plt.show()

# For any number of latent variables you can sample them and generate fake data
plt.figure(figsize = (size, size))
gs1 = gridspec.GridSpec(size, size)
gs1.update(wspace=0.0, hspace=0.0) # set the spacing between axes. 

for i in range(size):
    for j in range(size):
        plt.subplot(gs1[size*i + j])
        plt.axis('off')
        image = 1.0 - visualize(np.random.normal(0, 1.0, size = n_latent))
        plt.imshow(image.reshape((28, 28)), cmap = cm.Greys_r)
plt.show()

print("--- %s seconds ---" % (time.time() - start_time))
