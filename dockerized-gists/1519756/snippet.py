#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt


class RidgeRegressor(object):
    """
    Linear Least Squares Regression with Tikhonov regularization.
    More simply called Ridge Regression.

    We wish to fit our model so both the least squares residuals and L2 norm
    of the parameters are minimized.
    argmin Theta ||X*Theta - y||^2 + alpha * ||Theta||^2

    A closed form solution is available.
    Theta = (X'X + G'G)^-1 X'y

    Where X contains the independent variables, y the dependent variable and G
    is matrix alpha * I, where alpha is called the regularization parameter.
    When alpha=0 the regression is equivalent to ordinary least squares.

    http://en.wikipedia.org/wiki/Linear_least_squares_(mathematics)
    http://en.wikipedia.org/wiki/Tikhonov_regularization
    http://en.wikipedia.org/wiki/Ordinary_least_squares
    """

    def fit(self, X, y, alpha=0):
        """
        Fits our model to our training data.

        Arguments
        ----------
        X: mxn matrix of m examples with n independent variables
        y: dependent variable vector for m examples
        alpha: regularization parameter. A value of 0 will model using the
        ordinary least squares regression.
        """
        X = np.hstack((np.ones((X.shape[0], 1)), X))
        G = alpha * np.eye(X.shape[1])
        G[0, 0] = 0  # Don't regularize bias
        self.params = np.dot(np.linalg.inv(np.dot(X.T, X) + np.dot(G.T, G)),
                             np.dot(X.T, y))

    def predict(self, X):
        """
        Predicts the dependent variable of new data using the model.
        The assumption here is that the new data is iid to the training data.

        Arguments
        ----------
        X: mxn matrix of m examples with n independent variables
        alpha: regularization parameter. Default of 0.

        Returns
        ----------
        Dependent variable vector for m examples
        """
        X = np.hstack((np.ones((X.shape[0], 1)), X))
        return np.dot(X, self.params)


if __name__ == '__main__':
    # Create synthetic data
    X = np.linspace(0, 6, 100)
    y = 1 + 2 * np.sin(X)
    yhat = y + .5 * np.random.normal(size=len(X))

    # Plot synthetic data
    plt.plot(X, y, 'g', label='y = 1 + 2 * sin(x)')
    plt.plot(X, yhat, 'rx', label='noisy samples')

    # Create feature matrix
    tX = np.array([X]).T
    tX = np.hstack((tX, np.power(tX, 2), np.power(tX, 3)))

    # Plot regressors
    r = RidgeRegressor()
    r.fit(tX, y)
    plt.plot(X, r.predict(tX), 'b', label=u'ŷ (alpha=0.0)')
    alpha = 3.0
    r.fit(tX, y, alpha)
    plt.plot(X, r.predict(tX), 'y', label=u'ŷ (alpha=%.1f)' % alpha)

    plt.legend()
    plt.show()
