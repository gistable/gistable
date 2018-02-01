import theano
import theano.tensor as T
from theano.tensor.shared_randomstreams import RandomStreams
from theano.sandbox.rng_mrg import MRG_RandomStreams
from lasagne.updates import adam
from lasagne.utils import collect_shared_vars

from sklearn.datasets import fetch_mldata
from sklearn.cross_validation import train_test_split
from sklearn import preprocessing

import numpy as np


rnd = RandomStreams(seed=123)
gpu_rnd = MRG_RandomStreams(seed=123)


def nonlinearity(x):
    return T.nnet.relu(x)


def log_gaussian(x, mu, sigma):
    return -0.5 * np.log(2 * np.pi) - T.log(T.abs_(sigma)) - (x - mu) ** 2 / (2 * sigma ** 2)


def log_gaussian_logsigma(x, mu, logsigma):
    return -0.5 * np.log(2 * np.pi) - logsigma / 2. - (x - mu) ** 2 / (2. * T.exp(logsigma))


def _shared_dataset(data_xy, borrow=True):
    data_x, data_y = data_xy
    shared_x = theano.shared(np.asarray(data_x, dtype=theano.config.floatX), borrow=borrow)
    shared_y = theano.shared(np.asarray(data_y, dtype=theano.config.floatX), borrow=borrow)
    return shared_x, shared_y


def init(shape):
    return np.asarray(
        np.random.normal(0, 0.05, size=shape),
        dtype=theano.config.floatX
    )


def get_random(shape, avg, std):
    return gpu_rnd.normal(shape, avg=avg, std=std)


if __name__ == '__main__':
    mnist = fetch_mldata('MNIST original')
    # prepare data
    N = 5000

    data = np.float32(mnist.data[:]) / 255.
    idx = np.random.choice(data.shape[0], N)
    data = data[idx]
    target = np.int32(mnist.target[idx]).reshape(N, 1)

    train_idx, test_idx = train_test_split(np.array(range(N)), test_size=0.05)
    train_data, test_data = data[train_idx], data[test_idx]
    train_target, test_target = target[train_idx], target[test_idx]

    train_target = np.float32(preprocessing.OneHotEncoder(sparse=False).fit_transform(train_target))

    # inputs
    x = T.matrix('x')
    y = T.matrix('y')
    n_input = train_data.shape[1]
    M = train_data.shape[0]
    sigma_prior = T.exp(-3)
    n_samples = 3
    learning_rate = 0.001
    n_epochs = 100

    # weights
    # L1
    n_hidden_1 = 200
    W1_mu = theano.shared(value=init((n_input, n_hidden_1)))
    W1_logsigma = theano.shared(value=init((n_input, n_hidden_1)))
    b1_mu = theano.shared(value=init((n_hidden_1,)))
    b1_logsigma = theano.shared(value=init((n_hidden_1,)))

    # L2
    n_hidden_2 = 200
    W2_mu = theano.shared(value=init((n_hidden_1, n_hidden_2)))
    W2_logsigma = theano.shared(value=init((n_hidden_1, n_hidden_2)))
    b2_mu = theano.shared(value=init((n_hidden_2,)))
    b2_logsigma = theano.shared(value=init((n_hidden_2,)))

    # L3
    n_output = 10
    W3_mu = theano.shared(value=init((n_hidden_2, n_output)))
    W3_logsigma = theano.shared(value=init((n_hidden_2, n_output)))
    b3_mu = theano.shared(value=init((n_output,)))
    b3_logsigma = theano.shared(value=init((n_output,)))

    all_params = [
        W1_mu, W1_logsigma, b1_mu, b1_logsigma,
        W2_mu, W2_logsigma, b2_mu, b2_logsigma,
        W3_mu, W3_logsigma, b3_mu, b3_logsigma
    ]
    all_params = collect_shared_vars(all_params)

    # building the objective
    # remember, we're evaluating by samples
    log_pw, log_qw, log_likelihood = 0., 0., 0.

    for _ in xrange(n_samples):

        epsilon_w1 = get_random((n_input, n_hidden_1), avg=0., std=sigma_prior)
        epsilon_b1 = get_random((n_hidden_1,), avg=0., std=sigma_prior)

        W1 = W1_mu + T.log(1. + T.exp(W1_logsigma)) * epsilon_w1
        b1 = b1_mu + T.log(1. + T.exp(b1_logsigma)) * epsilon_b1

        epsilon_w2 = get_random((n_hidden_1, n_hidden_2), avg=0., std=sigma_prior)
        epsilon_b2 = get_random((n_hidden_2,), avg=0., std=sigma_prior)

        W2 = W2_mu + T.log(1. + T.exp(W2_logsigma)) * epsilon_w2
        b2 = b2_mu + T.log(1. + T.exp(b2_logsigma)) * epsilon_b2

        epsilon_w3 = get_random((n_hidden_2, n_output), avg=0., std=sigma_prior)
        epsilon_b3 = get_random((n_output,), avg=0., std=sigma_prior)

        W3 = W3_mu + T.log(1. + T.exp(W3_logsigma)) * epsilon_w3
        b3 = b3_mu + T.log(1. + T.exp(b3_logsigma)) * epsilon_b3

        a1 = nonlinearity(T.dot(x, W1) + b1)
        a2 = nonlinearity(T.dot(a1, W2) + b2)
        h = T.nnet.softmax(nonlinearity(T.dot(a2, W3) + b3))

        sample_log_pw, sample_log_qw, sample_log_likelihood = 0., 0., 0.

        for W, b, W_mu, W_logsigma, b_mu, b_logsigma in [(W1, b1, W1_mu, W1_logsigma, b1_mu, b1_logsigma),
                                                         (W2, b2, W2_mu, W2_logsigma, b2_mu, b2_logsigma),
                                                         (W3, b3, W3_mu, W3_logsigma, b3_mu, b3_logsigma)]:

            # first weight prior
            sample_log_pw += log_gaussian(W, 0., sigma_prior).sum()
            sample_log_pw += log_gaussian(b, 0., sigma_prior).sum()

            # then approximation
            sample_log_qw += log_gaussian_logsigma(W, W_mu, W_logsigma * 2).sum()
            sample_log_qw += log_gaussian_logsigma(b, b_mu, b_logsigma * 2).sum()

        # then the likelihood
        sample_log_likelihood = log_gaussian(y, h, sigma_prior).sum()

        log_pw += sample_log_pw
        log_qw += sample_log_qw
        log_likelihood += sample_log_likelihood

    log_qw /= n_samples
    log_pw /= n_samples
    log_likelihood /= n_samples

    batch_size = 100
    n_batches = M / float(batch_size)

    objective = ((1. / n_batches) * (log_qw - log_pw) - log_likelihood).sum() / float(batch_size)

    # updates

    updates = adam(objective, all_params, learning_rate=learning_rate)

    i = T.iscalar()

    train_data = theano.shared(np.asarray(train_data, dtype=theano.config.floatX))
    train_target = theano.shared(np.asarray(train_target, dtype=theano.config.floatX))

    train_function = theano.function(
        inputs=[i],
        outputs=objective,
        updates=updates,
        givens={
            x: train_data[i * batch_size: (i + 1) * batch_size],
            y: train_target[i * batch_size: (i + 1) * batch_size]
        }
    )

    a1_mu = nonlinearity(T.dot(x, W1_mu) + b1_mu)
    a2_mu = nonlinearity(T.dot(a1_mu, W2_mu) + b2_mu)
    h_mu = T.nnet.softmax(nonlinearity(T.dot(a2_mu, W3_mu) + b3_mu))

    output_function = theano.function([x], T.argmax(h_mu, axis=1))

    n_train_batches = int(train_data.get_value().shape[0] / float(batch_size))

    # and finally, training loop
    for e in xrange(n_epochs):
        errs = []
        for b in xrange(n_train_batches):
            batch_err = train_function(b)
            errs.append(batch_err)
        out = output_function(test_data)
        acc = np.count_nonzero(output_function(test_data) == np.int32(test_target.ravel())) / float(test_data.shape[0])
        print 'epoch', e, 'cost', np.mean(errs), 'Accuracy', acc
