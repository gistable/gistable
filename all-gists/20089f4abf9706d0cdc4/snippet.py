# Implementation of a simple MLP network with one hidden layer. Tested on the iris data set.
# Requires: numpy, sklearn, theano

# NOTE: In order to make the code simple, we rewrite x * W_1 + b_1 = x' * W_1' 
# where x' = [x | 1] and W_1' is the matrix W_1 appended with a new row with elements b_1's. 
# Similarly, for h * W_2 + b_2
import theano
from theano import tensor as T
import numpy as np
from sklearn import datasets
from sklearn.cross_validation import train_test_split

def init_weights(shape):
    """ Weight initialization """
    weights = np.asarray(np.random.randn(*shape) * 0.01, dtype=theano.config.floatX)
    return theano.shared(weights)

def backprop(cost, params, lr=0.01):
    """ Back-propagation """
    grads   = T.grad(cost=cost, wrt=params)
    updates = []
    for p, g in zip(params, grads):
        updates.append([p, p - g * lr])
    return updates

def forwardprop(X, w_1, w_2):
    """ Forward-propagation """
    h    = T.nnet.sigmoid(T.dot(X, w_1))  # The \sigma function
    yhat = T.nnet.softmax(T.dot(h, w_2))  # The \varphi function
    return yhat

def get_iris_data():
    """ Read the iris data set and split them into training and test sets """
    iris   = datasets.load_iris()
    data   = iris.data
    target = iris.target

    # Prepend the column of 1s for bias
    N, M  = data.shape
    all_X = np.ones((N, M + 1))
    all_X[:, 1:] = data

    # Convert into one-hot vectors
    num_labels = len(np.unique(target))
    all_Y = np.eye(num_labels)[target]  # One liner trick!
    return train_test_split(all_X, all_Y, test_size=0.33)

if __name__ == '__main__':
    train_X, test_X, train_y, test_y = get_iris_data()

    # Symbols
    X = T.fmatrix()
    Y = T.fmatrix()

    # Layer's sizes
    x_size = train_X.shape[1]             # Number of input nodes: 4 features and 1 bias
    h_size = 256                          # Number of hidden nodes
    y_size = train_y.shape[1]             # Number of outcomes (3 iris flowers)
    w_1 = init_weights((x_size, h_size))  # Weight initializations
    w_2 = init_weights((h_size, y_size))

    # Forward propagation
    yhat   = forwardprop(X, w_1, w_2)

    # Backward propagation
    cost    = T.mean(T.nnet.categorical_crossentropy(yhat, Y))
    params  = [w_1, w_2]
    updates = backprop(cost, params)

    # Train and predict
    train   = theano.function(inputs=[X, Y], outputs=cost, updates=updates, allow_input_downcast=True)
    pred_y  = T.argmax(yhat, axis=1)
    predict = theano.function(inputs=[X], outputs=pred_y, allow_input_downcast=True)

    # Run SGD
    for iter in range(500):
        for i in range(len(train_X)):
            train(train_X[i: i + 1], train_y[i: i + 1])
        train_accuracy = np.mean(np.argmax(train_y, axis=1) == predict(train_X))
        test_accuracy  = np.mean(np.argmax(test_y, axis=1) == predict(test_X))
        print("Iteration = %d, train accuracy = %.2f%%, test accuracy = %.2f%%"
              % (iter + 1, 100 * train_accuracy, 100 * test_accuracy))
