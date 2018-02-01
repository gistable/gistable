# Author: Kyle Kastner
# License: BSD 3-clause
# THEANO_FLAGS="optimizer=None,compute_test_value=raise" python tanh_rnn.py
import numpy as np
import theano
import theano.tensor as T
from scipy import linalg


class sgd(object):
    # Only here for API conformity with other optimizers
    def __init__(self, params):
        pass

    def updates(self, params, grads, learning_rate):
        updates = []
        for n, (param, grad) in enumerate(zip(params, grads)):
            updates.append((param, param - learning_rate * grad))
        return updates


def np_zeros(shape):
    """ Builds a numpy variable filled with zeros """
    return np.zeros(shape).astype(theano.config.floatX)


def np_rand(shape, rng):
    """ Builds a numpy variable filled with random values """
    return (0.01 * (rng.rand(*shape) - 0.5)).astype(theano.config.floatX)


def np_ortho(shape, rng, name=None):
    """ Builds a numpy variable filled with orthonormal random values """
    g = rng.randn(*shape)
    o_g = linalg.svd(g)[0]
    return o_g.astype(theano.config.floatX)


minibatch_size = 4
# number of input units
n_in = 1
# number of hidden units
n_hid = 20
# number of output units
n_out = 1

# Generate sinewaves offset in phase
n_timesteps = 50
n_full = 10 * n_timesteps
d1 = 3 * np.arange(n_full) / (2 * np.pi)
d2 = 3 * np.arange(minibatch_size) / (2 * np.pi)
full_sines = np.sin(np.array([d1] * minibatch_size).T + d2)
# Uncomment to add harmonics
#full_sines += np.sin(np.array([1.7 * d1] * minibatch_size).T + d2)
#full_sines += np.sin(np.array([7.362 * d1] * minibatch_size).T + d2)
# Uncomment to switch to square waves
#full_sines[full_sines <= 0] = 0
#full_sines[full_sines > 0] = 1
full_sines = full_sines[:, :, None]

# Setup dataset and initial hidden vector of zeros
all_sines = full_sines[:n_timesteps]
X = all_sines[:-1]
y = all_sines[1:]
h_init = np_zeros((minibatch_size, n_hid))

# input (where first dimension is time)
X_sym = T.tensor3()
# target (where first dimension is time)
y_sym = T.tensor3()
# initial hidden state of the RNN
h0 = T.dmatrix()

# tag.test_value is crucial for debugging! Run the script with
# THEANO_FLAGS="compute_test_value=raise,optimizer=None"
# for cleaner debugging
X_sym.tag.test_value = X[:10]
y_sym.tag.test_value = y[:10]
h0.tag.test_value = h_init

# Using checked versions should allow for both float32 and float64 theano flags
X_check = T.cast(X_sym, theano.config.floatX)
y_check = T.cast(y_sym, theano.config.floatX)
h0_check = T.cast(h0, theano.config.floatX)

# Setup weights
random_state = np.random.RandomState(1999)
# Orthogonal initialization is good for recurrent (square) matrices!
# Advances in Optimizing Recurrent Networks
# Bengio, Boulanger-Lewandowski, Pascanu
# Section 2
# http://arxiv.org/pdf/1212.0901v2.pdf
# U stores information necessary for GRU
W_hid_np = np_ortho((n_hid, n_hid), random_state)
W_in_np = np_rand((n_in, n_hid), random_state)
b_in_np = np_zeros((n_hid,))
W_out_np = np_rand((n_hid, n_out), random_state)
b_out_np = np_zeros((n_out,))

# hidden to hidden weights
W_hid = theano.shared(W_hid_np, borrow=True)
# input to hidden layer weights
W_in = theano.shared(W_in_np, borrow=True)
# input to hidden bias
b_in = theano.shared(b_in_np, borrow=True)
# hidden to output layer weights
W_out = theano.shared(W_out_np, borrow=True)
# hidden to output bias
b_out = theano.shared(b_out_np, borrow=True)

# Begin model
# linear projection from input "into" recurrent
# do it here to better exploit parallelism
proj_X = T.dot(X_check, W_in) + b_in
theano.printing.Print("proj_X.shape")(proj_X.shape)

# recurrent function (using tanh activation function)
def step(in_t, h_tm1, W_hid):
    h_t = T.tanh(in_t + T.dot(h_tm1, W_hid))
    theano.printing.Print("h_t.shape")(h_t.shape)
    return h_t

# Another debug tip - try calling your scan function directly to debug internals
# step(X_check[0], h0_check, W_in, W_hid)

# the hidden state `h` for the entire sequence
h, _ = theano.scan(step,
                   sequences=[proj_X],
                   outputs_info=[h0_check],
                   non_sequences=[W_hid])
theano.printing.Print("h.shape")(h.shape)

# linear output activation
y_hat = T.dot(h, W_out) + b_out
theano.printing.Print("y_hat.shape")(y_hat.shape)

# Parameters of the model
params = [W_in, b_in, W_hid, W_out, b_out]
# error between output and target
cost = ((y_check - y_hat) ** 2).sum()
# gradients on the weights using BPTT
grads = T.grad(cost, params)

# Use stochastic gradient descent to optimize
opt = sgd(params)
learning_rate = 0.001
updates = opt.updates(params, grads, learning_rate)

# By returning h we can train while preserving hidden state from previous
# samples. This can allow for truncated backprop through time (TBPTT)!
fit_function = theano.function([X_sym, y_sym, h0], [cost, h], updates=updates)
predict_function = theano.function([X_sym, h0], [y_hat, h])

epochs = 2000
# Print 50 status updates along with last
status_points = list(range(epochs))
status_points = status_points[::epochs // 50] + [status_points[-1]]
for i in range(epochs):
    ii = np.arange(minibatch_size).astype("int32")
    random_state.shuffle(ii)
    Xi = X[:, ii]
    yi = y[:, ii]
    pred, _ = predict_function(Xi, h_init)
    err, _ = fit_function(Xi, yi, h_init)
    if i in status_points:
        print("Epoch %i: err %f" % (i, err))

# Run on self generations
n_seed = n_timesteps // 4
X_grow = X[:n_seed]
for i in range(n_timesteps // 4, n_full):
    p, _ = predict_function(X_grow, h_init)
    # take last prediction only
    X_grow = np.concatenate((X_grow, p[-1][None]))

import matplotlib.pyplot as plt
f, axarr1 = plt.subplots(minibatch_size)
for i in range(minibatch_size):
    # -1 to have the same dims
    axarr1[i].plot(full_sines[:-1, i, 0], color="steelblue")

f, axarr2 = plt.subplots(minibatch_size)
for i in range(minibatch_size):
    axarr2[i].plot(p[:, i, 0], color="darkred")
plt.show()
