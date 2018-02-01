# Toy examples that demonstrate how to configure
# nolearn.lasagne.NeuralNet and what data to send in for
# classification problems with single and multiple classes, and
# regression problems with and without multiple targets.

from lasagne.layers import DenseLayer
from lasagne.layers import InputLayer
from lasagne.nonlinearities import softmax
from nolearn.lasagne import NeuralNet
import numpy as np
from sklearn.datasets import make_classification
from sklearn.datasets import make_regression


def classif(X, y):
    l = InputLayer(shape=(None, X.shape[1]))
    l = DenseLayer(l, num_units=len(np.unique(y)), nonlinearity=softmax)
    net = NeuralNet(l, update_learning_rate=0.01)
    net.fit(X, y)
    print(net.score(X, y))


def regr(X, y):
    l = InputLayer(shape=(None, X.shape[1]))
    l = DenseLayer(l, num_units=y.shape[1], nonlinearity=None)
    net = NeuralNet(l, regression=True, update_learning_rate=0.01)
    net.fit(X, y)
    print(net.score(X, y))


def main():
    # Classification with two classes:
    X, y = make_classification()
    y = y.astype(np.int32)
    classif(X, y)

    # Classification with ten classes:
    X, y = make_classification(n_classes=10, n_informative=10)
    y = y.astype(np.int32)
    classif(X, y)

    # Regression with one target:
    X, y = make_regression()
    y = y.reshape(-1, 1).astype(np.float32)
    regr(X, y)

    # Regression with ten targets:
    X, y = make_regression(n_targets=10)
    y = y.astype(np.float32)
    regr(X, y)


if __name__ == '__main__':
    main()
