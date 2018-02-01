"""
Non-Negative Garotte implementation with the scikit-learn
"""

# Author: Alexandre Gramfort <alexandre.gramfort@inria.fr>
#         Jaques Grobler (__main__ script) <jaques.grobler@inria.fr>
#
# License: BSD Style.

import numpy as np


from sklearn.linear_model.base import LinearModel
from sklearn.linear_model import LinearRegression, Lasso, lasso_path


def non_negative_garotte(X, y, alpha, tol=0.001):
    coef_ols = LinearRegression(fit_intercept=False).fit(X, y).coef_

    X = X * coef_ols[np.newaxis, :]
    shrink_coef = Lasso(alpha=alpha, fit_intercept=False,
                        positive=True, normalize=False,
                        tol=tol).fit(X, y).coef_

    # Shrunken betas
    coef = coef_ols * shrink_coef

    # Residual Sum of Squares
    rss = np.sum((y - np.dot(X, coef)) ** 2)
    return coef, shrink_coef, rss


def non_negative_garotte_path(X, y, eps=1e-3, n_alphas=100, alphas=None,
                   precompute='auto', **params):
    coef_ols = LinearRegression(fit_intercept=False).fit(X, y).coef_

    X = X * coef_ols[np.newaxis, :]

    # Use lars_path even if it does not support positivity (much faster)
    _, _, shrink_coef_path = lars_path(X, y, method='lasso')

    # models = lasso_path(X, y, eps, n_alphas, alphas=None,
    #            precompute=precompute, Xy=None, fit_intercept=False,
    #            normalize=False, copy_X=True, verbose=False,
    #            **params)
    #
    # shrink_coef_path = np.array([m.coef_ for m in models]).T

    coef_path = shrink_coef_path * coef_ols[:, None]

    # Residual Sum of Squares
    rss_path = np.sum((y[:, None] - np.dot(X, coef_path)) ** 2, axis=0)

    return coef_path, shrink_coef_path, rss_path


class NonNegativeGarrote(LinearModel):
    """NonNegativeGarrote

    Ref:
    Breiman, L. (1995), "Better Subset Regression Using the Nonnegative
    Garrote," Technometrics, 37, 373-384. [349,351]
    """
    def __init__(self, alpha, fit_intercept=True, tol=1e-4, normalize=False,
                 copy_X=True):
        self.alpha = alpha
        self.fit_intercept = fit_intercept
        self.tol = tol
        self.normalize = normalize
        self.copy_X = copy_X

    def fit(self, X, y):

        X, y, X_mean, y_mean, X_std = self._center_data(X, y,
                self.fit_intercept, self.normalize, self.copy_X)

        self.coef_, self.shrink_coef_, self.rss_ = \
                                    non_negative_garotte(X, y, self.alpha)
        self._set_intercept(X_mean, y_mean, X_std)



if __name__ == '__main__':
    import pylab as pl
    from sklearn.utils import check_random_state
    from sklearn.linear_model import lars_path

    rng = check_random_state(None)

    max_samples = 501
    sample_size_range = xrange(25, max_samples, 25)

    # true path
    coef = np.array([1, 1, 0])

    # for 4 different values of alpha
    for alpha_val, fig_num in ((0.35, 1), (0.45, 2), (0.55, 3), (0.65, 4)):
        # lists for plotting the two techniques results
        hits_lars = []
        hits_ng = []

        print 'for alpha = ', alpha_val
        # set up plots
        pl.figure(fig_num, figsize=(5, 5))
        pl.clf
        pl.axis('tight')
        pl.title('alpha = %.2f' % alpha_val )
        pl.xlabel('Sample Size')
        pl.ylabel('Frequency of Selecting Correct Models')

        # vary the sample size from 25 up until 500
        for sample_size in sample_size_range:
            ng_path_correct = 0
            lars_path_correct = 0

            # create 100 data sets to test
            for dataset_iter in xrange(100):
                # create a dataset
                X1 = rng.randn(sample_size)
                X2 = rng.randn(sample_size)
                X3 = np.sqrt(1 - 2 * alpha_val ** 2) * rng.randn(sample_size) \
                    + alpha_val * (X1 + X2)
                X = np.c_[X1, X2, X3]
                y = np.dot(X, [1, 1, 0])

                # get the lasso's coefficients
                alphas, _, coefs = lars_path(X, y, method='lasso')
                # get the non-negative garotte's coefficients
                ng_coefs, _, _ = non_negative_garotte_path(X, y, eps=1e-5)

                # test if either model's solution path matches the orinial model
                if np.any(np.all(ng_coefs.astype(np.bool) == coef.astype(np.bool)[:, np.newaxis], axis=0)):
                    ng_path_correct += 1
                if np.any(np.all(coefs.astype(np.bool) == coef.astype(np.bool)[:, np.newaxis], axis=0)):
                    lars_path_correct += 1

            hits_lars.append(lars_path_correct / 100.)
            hits_ng.append(ng_path_correct / 100.)

        pl.plot(sample_size_range, hits_lars, 'r-')
        pl.plot(sample_size_range, hits_ng, 'b-')
        pl.xlim([0, max_samples])
        pl.ylim([0, 1.1])

    pl.show()
