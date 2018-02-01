"""A stripped-down MLP example, using Theano.

Based on the tutorial here: http://deeplearning.net/tutorial/mlp.html

This example trims away some complexities, and makes it easier to see how Theano works.

Design changes:

* Model compiled in a distinct function, so that symbolic variables are not in run-time scope.
* No classes. Network shown by chained function calls.

Some features of original have been dropped:

* Inputs streamed to model, not pre-loaded as given
* Minibatch size 1, i.e. `true' stochastic update
* No early stopping

Released under MIT license
Copyright Matthew Honnibal, 2015.
"""
import os
import sys
import time
from os import path

import numpy

import theano
import theano.tensor as T
import gzip
import cPickle


def load_data(dataset):
    ''' Loads the dataset

    :type dataset: string
    :param dataset: the path to the dataset (here MNIST)
    '''
    # Download the MNIST dataset if it is not present
    data_dir, data_file = os.path.split(dataset)
    if data_dir == "" and not os.path.isfile(dataset):
        # Check if dataset is in the data directory.
        data_dir = os.path.join(os.path.split(__file__)[0], "..", "data")
        if not path.exists(data_dir):
            print "No data directory to save data to. Try:"
            print "mkdir ../data"
            sys.exit(1)
        new_path = path.join(data_dir, data_file)
        if os.path.isfile(new_path) or data_file == 'mnist.pkl.gz':
            dataset = new_path

    if (not os.path.isfile(dataset)) and data_file == 'mnist.pkl.gz':
        import urllib
        url = 'http://www.iro.umontreal.ca/~lisa/deep/data/mnist/mnist.pkl.gz'
        print 'Downloading data from %s' % url
        urllib.urlretrieve(url, dataset)

    print '... loading data'

    # Load the dataset
    with gzip.open(dataset, 'rb') as f:
        train_set, valid_set, test_set = cPickle.load(f)
    return _make_array(train_set), _make_array(valid_set), _make_array(test_set)


def _make_array(xy):
    data_x, data_y = xy
    return zip(
        numpy.asarray(data_x, dtype=theano.config.floatX),
        numpy.asarray(data_y, dtype='int32'))


def _init_logreg_weights(n_hidden, n_out):
    weights = numpy.zeros((n_hidden, n_out), dtype=theano.config.floatX)
    bias = numpy.zeros((n_out,), dtype=theano.config.floatX)
    return (
        theano.shared(name='W', borrow=True, value=weights),
        theano.shared(name='b', borrow=True, value=bias)
    )


def _init_hidden_weights(n_in, n_out):
    rng = numpy.random.RandomState(1234)
    weights = numpy.asarray(
        rng.uniform(
            low=-numpy.sqrt(6. / (n_in + n_out)),
            high=numpy.sqrt(6. / (n_in + n_out)),
            size=(n_in, n_out)
        ),
        dtype=theano.config.floatX
    )
    bias = numpy.zeros((n_out,), dtype=theano.config.floatX)
    return (
        theano.shared(value=weights, name='W', borrow=True),
        theano.shared(value=bias, name='b', borrow=True)
    )


# Define how an input is fed through a layer of the network, and how a step of
# the stochastic gradient descent is computed.
    
# Note that these are *symbolic expressions* --- we are just compiling code here.
# These functions are only called during compile_model.  The *actual* feed-forward
# and SGD update procedures, which happen iteratively on each example, are 
# Theano-internal.
def feed_forward(activation, weights, bias, input_):
    return activation(T.dot(input_, weights) + bias)

def sgd_step(param, cost, learning_rate):
    return param - (learning_rate * T.grad(cost, param))

# These are also symbolic.
def L1(L1_reg, w1, w2):
    return L1_reg * (abs(w1).sum() + abs(w2).sum())


def L2(L2_reg, w1, w2):
    return L2_reg * ((w1 ** 2).sum() + (w2 ** 2).sum())
 

def compile_model(n_in, n_classes, n_hidden, learning_rate, L1_reg, L2_reg):
    '''Compile train and evaluation functions, which we'll then call iteratively
    to train the parameters.  This function is called exactly once --- think of
    it like a compiler.  We declare variables, allocate memory, and define some
    computation.
    '''
    # allocate symbolic variables for the data
    x = T.vector('x')  # Features
    y = T.iscalar('y') # (Gold) Label
    
    # Allocate and initialize weights.  These are stored internally, and updated.
    hidden_W, hidden_b = _init_hidden_weights(n_in, n_hidden)
    logreg_W, logreg_b = _init_logreg_weights(n_hidden, n_classes)

    # Estimate P(y | x) given the current weights
    p_y_given_x = feed_forward(
                      T.nnet.softmax,
                      logreg_W,
                      logreg_b,
                      feed_forward(
                          T.tanh,
                          hidden_W,
                          hidden_b,
                          x)) # <--- Our input variable (the features)

    cost = (
        -T.log(p_y_given_x[0, y]) # <-- Negative log likelihood of gold label
        + L1(L1_reg, logreg_W, hidden_W)
        + L2(L2_reg, logreg_W, hidden_W)
    )

    # Compile the training function.  Successive calls to this update the weights.
    # Internal state is maintained.
    # The output is "cost", which requires the computation of p_y_given_x.  We
    # also define how to update the weights based on the input label.
    train_model = theano.function(
        inputs=[x, y],
        outputs=cost, # <-- Output depends on cost, which depends on P(y | x)
        updates=[
            (logreg_W, sgd_step(logreg_W, cost, learning_rate)),
            (logreg_b, sgd_step(logreg_b, cost, learning_rate)),
            (hidden_W, sgd_step(hidden_W, cost, learning_rate)),
            (hidden_b, sgd_step(hidden_b, cost, learning_rate)),
        ]
    )

    # Compile the evaluation function, which returns a 0/1 loss wrt the true
    # label.  Note that the output depends on p_y_given_x, so the program must
    # compute it.
    evaluate_model = theano.function(
        inputs=[x, y],
        outputs=T.neq(y, T.argmax(p_y_given_x[0])),
    )
    return train_model, evaluate_model


def main(learning_rate=0.01, L1_reg=0.00, L2_reg=0.0001, n_epochs=1000,
             dataset='mnist.pkl.gz', n_hidden=500):
    train_examples, dev_examples, test_examples = load_data(dataset)
    print '... building the model'
    train_model, evaluate_model = compile_model(28*28, 10, n_hidden, learning_rate, L1_reg, L2_reg)
    print '... training'
    for epoch in range(1, n_epochs+1):
        for x, y in train_examples:
            train_model(x, y)
        # compute zero-one loss on validation set
        error = numpy.mean([evaluate_model(x, y) for x, y in dev_examples])
        print('epoch %i, validation error %f %%' % (epoch, error * 100))


if __name__ == '__main__':
    main()