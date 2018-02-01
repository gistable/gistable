#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This is a simplified implementation of the LSTM language model (by Graham Neubig)
#
#  LSTM Neural Networks for Language Modeling
#  Martin Sundermeyer, Ralf Schlüter, Hermann Ney
#  InterSpeech 2012
# 
# The structure of the model is extremely simple. At every time step we
# read in the one-hot vector for the previous word, and predict the next word.
# Most of the learning code is based on the full-gradient update for LSTMs
#
#  Framewise Phoneme Classification with Bidirectional LSTM and Other Neural Network Architectures
#  Alex Graves and Jurgen Schmidhuber
#  Neural Networks 2005
#
# Note that this code is optimized for simplicity, not speed or accuracy, so it will
# be slow, and not necessarily get excellent performance. Also, it has not been checked all that
# carefully, but the perplexity does seem to be going down, so it's probably ok?

from collections import defaultdict
import sys
import math
import numpy as np
from scipy import linalg
from scipy.special import expit         # Vectorized sigmoid function

# Initialize the random number generator
rng = np.random.RandomState(23455)

# Constants
NUM_EPOCHS = 10000    # Number of epochs
ALPHA = 1             # Learning rate
N = 10                # Number of units

# First read in the input
wids = defaultdict(lambda: len(wids))
wids['<BIAS>'] = 0
wids['<s>'] = 1
sents = []
words = 0

for line in sys.stdin:
    my_sent = ("<s> %s <s>" % line.strip()).split(' ')
    words += len(my_sent) - 2
    sents.append([wids[x] for x in my_sent])

# Define input-dependent variables
K = len(wids)       # Vocabulary size

# Set weights randomly and uniformly between [-0.1, 0.1]
W_iota_y = np.asarray(rng.uniform(low=-0.1, high=0.1, size=(N, N+K)))
W_iota_s = np.asarray(rng.uniform(low=-0.1, high=0.1, size=(N, 1)))
W_phi_y  = np.asarray(rng.uniform(low=-0.1, high=0.1, size=(N, N+K)))
W_phi_s  = np.asarray(rng.uniform(low=-0.1, high=0.1, size=(N, 1)))
W        = np.asarray(rng.uniform(low=-0.1, high=0.1, size=(N, N+K)))
W_eta_y  = np.asarray(rng.uniform(low=-0.1, high=0.1, size=(N, N+K)))
W_eta_s  = np.asarray(rng.uniform(low=-0.1, high=0.1, size=(N, 1)))
W_o      = np.asarray(rng.uniform(low=-0.1, high=0.1, size=(K, N)))

# Softmax function
def softmax(x):
    e = np.exp(x - np.max(x))  # prevent overflow
    return e / np.sum(e)

# Tanh and derivative
def tanh_prime(x):
    y = np.tanh(x)
    y_prime = 1 - (y * y)
    return y, y_prime

# For each epoch
last_ll = -1e99
for epoch_id in range(1, NUM_EPOCHS+1):
    epoch_ll = 0
    # For each sentence
    for sent_id, sent in enumerate(sents):
        ##### Initialize activations #####
        Tau = len(sent)
        I, X, Y, S              = range(Tau), range(Tau), range(Tau), range(Tau)
        X_iota, Y_iota, Yp_iota = range(Tau), range(Tau), range(Tau)
        X_phi, Y_phi, Yp_phi    = range(Tau), range(Tau), range(Tau)
        X_eta, Y_eta, Yp_eta    = range(Tau), range(Tau), range(Tau)
        G, Gp, H, Hp            = range(Tau), range(Tau), range(Tau), range(Tau)
        X_o, Y_o                = range(Tau), range(Tau)
        Y[0] = np.zeros( (N, 1) )
        S[0] = np.zeros( (N, 1) )
        sent_ll = 0 # Sentence log likelihood
        ##### Forward pass #####
        # For each time step
        for t in range(1, Tau):
            # Create the input vector
            I[t-1] = np.zeros((N+K, 1))
            I[t-1][0:N] += Y[t-1]
            I[t-1][N] = 1             # Bias
            I[t-1][N+sent[t-1]] = 1   # Word
            # Calculate input gate activations
            X_iota[t] = W_iota_y.dot(I[t-1]) + W_iota_s * S[t-1]
            Y_iota[t], Yp_iota[t] = tanh_prime(X_iota[t])
            # Calculate forget gate activations
            X_phi[t]  = W_phi_y.dot(I[t-1])  + W_phi_s  * S[t-1]
            Y_phi[t], Yp_phi[t] = tanh_prime(X_phi[t])
            # Calculate cells
            X[t] = W.dot(I[t-1])
            G[t], Gp[t] = tanh_prime(X[t])
            S[t] = Y_phi[t] * S[t-1] + Y_iota[t] * G[t]
            # Calculate output gate activations
            X_eta[t]  = W_eta_y.dot(I[t-1])  + W_eta_s  * S[t]
            Y_eta[t], Yp_eta[t] = tanh_prime(X_eta[t])
            # Calculate cell outputs
            H[t], Hp[t] = tanh_prime(S[t])
            Y[t] = Y_eta[t] * H[t]
            # Calculate the emission
            X_o[t] = W_o.dot(Y[t])
            Y_o[t] = softmax(X_o[t])
            sent_ll += math.log( max(Y_o[t][sent[t]],1e-20) )
        ##### Initialize gradient vectors #####
        Dg_o = np.zeros( (K, N) )
        Dg = np.zeros( (N, N+K) )
        Dg_eta_y = np.zeros( (N, N+K) )
        Dg_eta_s = np.zeros( (N, 1) )
        Dg_phi_y = np.zeros( (N, N+K) )
        Dg_phi_s = np.zeros( (N, 1) )
        Dg_iota_y = np.zeros( (N, N+K) )
        Dg_iota_s = np.zeros( (N, 1) )
        # Save the last deltas necessary
        Dl_last = np.zeros( (N, 1) )
        Dl_iota_last = np.zeros( (N, 1) )
        Dl_phi_last = np.zeros( (N, 1) )
        dE_last = np.zeros( (N, 1) )
        # Calculate the error and add it
        for t in reversed(range(1, len(sent))):
            # Calculate the error resulting from the output
            Dl_o = Y_o[t] * -1
            Dl_o[sent[t]] += 1
            Dg_o += Dl_o.dot(Y[t].T)
            # Calculate the epsilon
            Eps = W_o.T.dot(Dl_o) - W.T[0:N].dot(Dl_last)
            # Calculate the change in output gates
            Dl_eta = Yp_eta[t] * Eps * H[t]
            Dg_eta_y += Dl_eta.dot(I[t-1].T)
            Dg_eta_s += Dl_eta * S[t]
            # Calculate the derivative of the error
            dE = (Eps * Y_eta[t] * Hp[t] +
                  dE_last * Y_phi[t] +
                  Dl_iota_last * W_iota_s +
                  Dl_phi_last * W_phi_s +
                  Dl_eta * W_eta_s)
            # Calculate the delta of the states
            Dl = Y_iota[t] * Gp[t] * dE
            Dg += Dl.dot(I[t-1].T)
            # Calculate the delta of forget gate
            Dl_phi = Yp_phi[t] * dE * S[t-1]
            Dg_phi_y += Dl_phi.dot(I[t-1].T)
            Dg_phi_s += Dl_phi * S[t]
            # Calculate the delta of input gate
            Dl_iota = Yp_iota[t] * dE * S[t-1]
            Dg_iota_y += Dl_iota.dot(I[t-1].T)
            Dg_iota_s += Dl_iota * S[t]
            # Save the previous ones
            Dl_last = Dl
            Dl_iota_last = Dl_iota
            Dl_phi_last = Dl_phi
            dE_last = dE
        # Update weights
        W_o += ALPHA * Dg_o
        W += ALPHA * Dg
        W_eta_y += ALPHA * Dg_eta_y
        W_eta_s += ALPHA * Dg_eta_s
        W_phi_y += ALPHA * Dg_phi_y
        W_phi_s += ALPHA * Dg_phi_s
        W_iota_y += ALPHA * Dg_iota_y
        W_iota_s += ALPHA * Dg_iota_s
        # Print results
        epoch_ll += sent_ll
        # print(" Sentence %d LL: %f" % (sent_id, sent_ll))
    epoch_ent = epoch_ll*-math.log(2)/words
    epoch_ppl = 2 ** epoch_ent
    print("Epoch %d (alpha=%f) PPL=%f" % (epoch_id, ALPHA, epoch_ppl))
    if last_ll > epoch_ll:
        ALPHA /= 2.0
    last_ll = epoch_ll

# Print weights
print(W_o)
print(W)
print(W_eta_y)
print(W_eta_s)
print(W_phi_y)
print(W_phi_s)
print(W_iota_y)
print(W_iota_s)