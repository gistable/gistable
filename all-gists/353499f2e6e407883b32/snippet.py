"""
Simple implementation of Identity Recurrent Neural Networks (IRNN)

Reference
    A Simple Way to Initialize Recurrent Networks of Rectified Linear Units
    http://arxiv.org/abs/1504.00941

"""

import numpy as np
from theano import config, shared
from theano import scan


def load_mnist():
    from gzip import open
    from cPickle import load
    from os.path import join, dirname
    module_path = dirname(__file__)
    with open(join(module_path, 'mnist.pkl.gz')) as data_file:
        return load(data_file)


def shared_identity(size, scale=1):
    W = scale * np.eye(*size)
    return shared(np.asarray(W, dtype=config.floatX))


def shared_gaussian(size, scale=0.001):
    W = np.random.normal(scale=scale, size=size)
    return shared(np.asarray(W, dtype=config.floatX))


def shared_constant(size, scale=0):
    W = np.ones(shape=size, dtype=config.floatX) * scale
    return shared(np.asarray(W, dtype=config.floatX))


class RecurrentLayer(object):

    def __init__(self, input_size, output_size):
        self.W = shared_gaussian((input_size, output_size))
        self.W_hidden = shared_identity((output_size, output_size))
        self.h = shared_constant((batch_size, output_size))
        self.params = [self.W, self.W_hidden]

    def __call__(self, x, h):
        linear = T.dot(x, self.W) + T.dot(h, self.W_hidden)
        return T.switch(linear > 0, linear, 0)


class SoftmaxLayer(object):

    def __init__(self, input_size, output_size):
        self.W = shared_gaussian((input_size, output_size))
        self.b = shared_constant(output_size)
        self.params = [self.W, self.b]

    def __call__(self, x):
        return T.nnet.softmax(T.dot(x, self.W) + self.b)


def get_cost(x, y):
    x = x.T.reshape((784, -1, 1))
    results, updates = scan(recurrent_layer, x, recurrent_layer.h)
    predict_proba = softmax_layer(results[-1])
    return T.nnet.categorical_crossentropy(predict_proba, y).mean(), \
           T.mean(T.neq(T.argmax(predict_proba, axis=1), y))


def get_updates(cost, params):
    for param, grad in zip(params, T.grad(cost, params)):
        return [(param, param - learning_rate * T.clip(grad, -1, 1))]


def get_givens(X, y):
    batch_start = i * batch_size
    batch_end = (i+1) * batch_size
    X = shared(np.asarray(X, config.floatX))
    y = shared(np.asarray(y, 'int64'))
    return {x: X[batch_start:batch_end],
            t: y[batch_start:batch_end]}


if __name__ == '__main__':
    X, y = load_mnist()[0]

    from theano import tensor as T
    x = T.matrix()
    t = T.lvector()
    i = T.lscalar()

    learning_rate = 1e-8
    batch_size = 16

    recurrent_layer = RecurrentLayer(1, 100)
    softmax_layer = SoftmaxLayer(100, 10)

    cost, prediction_error = get_cost(x, t)
    params = recurrent_layer.params + softmax_layer.params
    updates = get_updates(cost, params)
    givens = get_givens(X, y)

    from theano import function
    fit = function([i], prediction_error, givens=givens)

    n_batches = len(X) / batch_size
    n_epochs = 1000

    for epoch in range(n_epochs):
        cost = []
        for batch in range(n_batches):
            cost.append(fit(batch))
        print np.mean(cost)