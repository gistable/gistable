#!/usr/bin/env python
from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
from numpy import newaxis, r_, c_, mat, e
from numpy.linalg import *

def plotData(X, y):
    #pos = (y.ravel() == 1).nonzero()
    #neg = (y.ravel() == 0).nonzero()
    pos = (y == 1).nonzero()[:1]
    neg = (y == 0).nonzero()[:1]

    plt.plot(X[pos, 0].T, X[pos, 1].T, 'k+', markeredgewidth=2, markersize=7)
    plt.plot(X[neg, 0].T, X[neg, 1].T, 'ko', markerfacecolor='r', markersize=7)

def sigmoid(z):
    g = 1. / (1 + e**(-z.A))
    return g

def costFunction(theta, X, y):
    m = X.shape[0]

    predictions = sigmoid(X * c_[theta])
    J = 1./m * (-y.T.dot(np.log(predictions)) - (1-y).T.dot(np.log(1 - predictions)))

    #grad = 1./m * X.T * (predictions - y)
    return J[0][0]##, grad.A

def predict(theta, X):
    p = sigmoid(X * c_[theta]) >= 0.5
    return p

def plotDecisionBoundary(theta, X, y):
    plotData(X[:, 1:3], y)

    if X.shape[1] <= 3:
        plot_x = r_[X[:,2].min()-2,  X[:,2].max()+2]
        plot_y = (-1./theta[2]) * (theta[1]*plot_x + theta[0])

        plt.plot(plot_x, plot_y)
        plt.legend(['Admitted', 'Not admitted', 'Decision Boundary'])
        plt.axis([30, 100, 30, 100])
    else:
        pass

if __name__ == '__main__':
    data = np.loadtxt('ex2data1.txt', delimiter=',')
    X = mat(c_[data[:, :2]])
    y = c_[data[:, 2]]

    # ============= Part 1: Plotting

    print 'Plotting data with + indicating (y = 1) examples and o ' \
          'indicating (y = 0) examples.'

    plotData(X, y)
    plt.ylabel('Exam 1 score')
    plt.xlabel('Exam 2 score')
    plt.legend(['Admitted', 'Not admitted'])
    plt.show()

    raw_input('Press any key to continue\n')

    # ============= Part 2: Compute cost and gradient

    m, n = X.shape

    X = c_[np.ones(m), X]

    initial_theta = np.zeros(n+1)

    cost, grad = costFunction(initial_theta, X, y), None

    print 'Cost at initial theta (zeros): %f' % cost
    print 'Gradient at initial theta (zeros):\n%s' % grad

    raw_input('Press any key to continue\n')

    # ============= Part 3: Optimizing using fminunc

    options = {'full_output': True, 'maxiter': 400}

    theta, cost, _, _, _ = \
        optimize.fmin(lambda t: costFunction(t, X, y), initial_theta, **options)

    print 'Cost at theta found by fminunc: %f' % cost
    print 'theta: %s' % theta

    plotDecisionBoundary(theta, X, y)
    plt.show()

    raw_input('Press any key to continue\n')

    # ============== Part 4: Predict and Accuracies

    prob = sigmoid(mat('1 45 85') * c_[theta])
    print 'For a student with scores 45 and 85, we predict an admission ' \
          'probability of %f' % prob

    p = predict(theta, X)
    print 'Train Accuracy:', (p == y).mean() * 100

    raw_input('Press any key to continue\n')
