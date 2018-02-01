# Start with
# THEANO_FLAGS='warn_float64=ignore,floatX=float64' python nntoy.py
# until I figure out how to coerce float32 vars within nolearn.

# Based on https://gist.github.com/dnouri/fe855653e9757e1ce8c4

# Toy examples that demonstrate how to configure
# nolearn.lasagne.NeuralNet and what data to send in for
# classification problems with single and multiple classes, and
# regression problems with and without multiple targets.

from lasagne.layers import DenseLayer
from lasagne.layers import InputLayer
from lasagne.nonlinearities import softmax
from lasagne.nonlinearities import tanh
from nolearn.lasagne import NeuralNet
from nolearn.lasagne import TrainSplit
import numpy as np

def my_make_classification(n, dim, n_classes):
    np.random.seed(0)
    X = np.random.normal(size=n*dim).astype(np.float32).reshape((n, dim))
    secrets = np.random.normal(size=n_classes*dim).astype(np.float32).reshape((dim, n_classes))
    secrets /= np.linalg.norm(secrets, axis=0) # normalize each column.
    product = X.dot(secrets)
    assert product.shape==(n, n_classes)
    y = np.argmin(product, axis=1)
    assert y.shape==(n,)
    return X, y

def my_make_regression(n, dim):
    X = np.random.normal(size=n*dim).astype(np.float32).reshape((n, dim))
    secret = np.random.normal(size=dim).astype(np.float32)
    y = X.dot(secret)
    return X, y

def classify(X, y):
    l = InputLayer(shape=(None, X.shape[1]))
    l = DenseLayer(l, num_units=100, nonlinearity=tanh)
    l = DenseLayer(l, num_units=len(np.unique(y)), nonlinearity=softmax)
    net = NeuralNet(l, update_learning_rate=0.05, train_split=TrainSplit(eval_size=0.2), verbose=1)
    net.fit(X, y)
    print(net.score(X, y))


def regress(X, y):
    l = InputLayer(shape=(None, X.shape[1]))
    l = DenseLayer(l, num_units=100, nonlinearity=tanh)
    l = DenseLayer(l, num_units=y.shape[1], nonlinearity=None)
    net = NeuralNet(l, regression=True, update_learning_rate=0.05, train_split=TrainSplit(eval_size=0.2), verbose=1)
    net.fit(X, y)
    print(net.score(X, y))


def main():
    # Classification with two classes:
    X, y = my_make_classification(n=10000, dim=10, n_classes=2)
    y = y.astype(np.int32)
    classify(X, y)

    # Classification with ten classes:
    X, y = my_make_classification(n=10000, dim=10, n_classes=10)
    y = y.astype(np.int32)
    classify(X, y)

    # Regression with one target:
    X, y = my_make_regression(n=10000, dim=10)
    y = y.reshape(-1, 1).astype(np.float32)
    regress(X, y)

if __name__ == '__main__':
    main()