# (C) Kyle Kastner, June 2014
# License: BSD 3 clause

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils import gen_batches
from scipy.linalg import eigh
from scipy.linalg import svd
import numpy as np

# From sklearn main
def svd_flip(u, v, u_based_decision=True):
    """Sign correction to ensure deterministic output from SVD.

    Adjusts the columns of u and the rows of v such that the loadings in the
    columns in u that are largest in absolute value are always positive.

    Parameters
    ----------
    u, v : ndarray
        u and v are the output of `linalg.svd` or
        `sklearn.utils.extmath.randomized_svd`, with matching inner dimensions
        so one can compute `np.dot(u * s, v)`.

    u_based_decision : boolean, (default=True)
        If True, use the columns of u as the basis for sign flipping. Otherwise,
        use the rows of v. The choice of which variable to base the decision on
        is generally algorithm dependent.


    Returns
    -------
    u_adjusted, v_adjusted : arrays with the same dimensions as the input.

    """
    if u_based_decision:
        # columns of u, rows of v
        max_abs_cols = np.argmax(np.abs(u), axis=0)
        signs = np.sign(u[max_abs_cols, xrange(u.shape[1])])
        u *= signs
        v *= signs[:, np.newaxis]
    else:
        # rows of v, columns of u
        max_abs_rows = np.argmax(np.abs(v), axis=1)
        signs = np.sign(v[xrange(v.shape[0]), max_abs_rows])
        u *= signs
        v *= signs[:, np.newaxis]
    return u, v


def _batch_mean_variance_update(X, old_mean, old_variance, old_sample_count):
    """Calculate an average mean update and a Youngs and Cramer variance update.

    From the paper "Algorithms for computing the sample variance: analysis and
    recommendations", by Chan, Golub, and LeVeque.

    Parameters
    ----------
    X : array-like, shape (n_samples, n_features)
        Data to use for variance update

    old_mean : array-like, shape: (n_features,)

    old_variance : array-like, shape: (n_features,)

    old_sample_count : int

    Returns
    -------
    updated_mean : array, shape (n_features,)

    updated_variance : array, shape (n_features,)

    updated_sample_count : int

    References
    ----------
    T. Chan, G. Golub, R. LeVeque. Algorithms for computing the sample variance:
        recommendations, The American Statistician, Vol. 37, No. 3, pp. 242-247

    """
    new_sum = X.sum(axis=0)
    new_variance = X.var(axis=0) * X.shape[0]
    old_sum = old_mean * old_sample_count
    n_samples = X.shape[0]
    updated_sample_count = old_sample_count + n_samples
    partial_variance = old_sample_count / (n_samples * updated_sample_count) * (
        n_samples / old_sample_count * old_sum - new_sum) ** 2
    unnormalized_variance = old_variance * old_sample_count + new_variance + \
        partial_variance
    return ((old_sum + new_sum) / updated_sample_count,
            unnormalized_variance / updated_sample_count,
            updated_sample_count)


class _CovZCA(BaseEstimator, TransformerMixin):
    def __init__(self, n_components=None, bias=.1, copy=True):
        self.n_components = n_components
        self.bias = bias
        self.copy = copy

    def fit(self, X, y=None):
        if self.copy:
            X = np.array(X, copy=self.copy)
        n_samples, n_features = X.shape
        self.mean_ = np.mean(X, axis=0)
        X -= self.mean_
        U, S, VT = svd(np.dot(X.T, X) / n_samples, full_matrices=False)
        components = np.dot(VT.T * np.sqrt(1.0 / (S + self.bias)), VT)
        self.components_ = components[:self.n_components]
        return self

    def transform(self, X):
        if self.copy:
            X = np.array(X, copy=self.copy)
        X -= self.mean_
        X_transformed = np.dot(X, self.components_.T)
        return X_transformed


class ZCA(BaseEstimator, TransformerMixin):
    """
    Identical to CovZCA up to scaling due to lack of division by n_samples
    S ** 2 / n_samples should correct this but components_ come out different
    though transformed examples are identical.
    """
    def __init__(self, n_components=None, bias=.1, copy=True):
        self.n_components = n_components
        self.bias = bias
        self.copy = copy

    def fit(self, X, y=None):
        if self.copy:
            X = np.array(X, copy=self.copy)
        n_samples, n_features = X.shape
        self.mean_ = np.mean(X, axis=0)
        X -= self.mean_
        U, S, VT = svd(X, full_matrices=False)
        components = np.dot(VT.T * np.sqrt(1.0 / (S ** 2 + self.bias)), VT)
        self.components_ = components[:self.n_components]
        return self

    def transform(self, X):
        if self.copy:
            X = np.array(X, copy=self.copy)
            X = np.copy(X)
        X -= self.mean_
        X_transformed = np.dot(X, self.components_.T)
        return X_transformed

import scipy
X = scipy.misc.lena()
zca = ZCA()
czca = _CovZCA()
X_zca = zca.fit_transform(X)
X_czca = czca.fit_transform(X)
from IPython import embed; embed()
raise ValueError()


class IncrementalCovZCA(BaseEstimator, TransformerMixin):
    def __init__(self, n_components=None, batch_size=None, bias=.1,
                 scale_by=1., copy=True):
        self.n_components = n_components
        self.batch_size = batch_size
        self.bias = bias
        self.scale_by = scale_by
        self.copy = copy
        self.scale_by = float(scale_by)
        self.mean_ = None
        self.covar_ = None
        self.n_samples_seen_ = 0.

    def fit(self, X, y=None):
        self.mean_ = None
        self.covar_ = None
        self.n_samples_seen_ = 0.
        n_samples, n_features = X.shape
        if self.batch_size is None:
            self.batch_size_ = 5 * n_features
        else:
            self.batch_size_ = self.batch_size
        for batch in gen_batches(n_samples, self.batch_size_):
            self.partial_fit(X[batch])
        return self

    def partial_fit(self, X):
        self.components_ = None
        if self.copy:
            X = np.array(X, copy=self.copy)
            X = np.copy(X)
        X /= self.scale_by
        n_samples, n_features = X.shape
        batch_mean = np.mean(X, axis=0)
        # Doing this without subtracting mean results in numerical instability
        # will have to play some games to work around this
        if self.mean_ is None:
            X -= batch_mean
            batch_covar = np.dot(X.T, X)
            self.mean_ = batch_mean
            self.covar_ = batch_covar
            self.n_samples_seen_ += float(n_samples)
        else:
            prev_mean = self.mean_
            prev_sample_count = self.n_samples_seen_
            prev_scale = self.n_samples_seen_ / (self.n_samples_seen_
                                                 + n_samples)
            update_scale = n_samples / (self.n_samples_seen_ + n_samples)
            self.mean_ = self.mean_ * prev_scale + batch_mean * update_scale

            X -= batch_mean
            # All of this correction is to minimize numerical instability in
            # the dot product
            batch_covar = np.dot(X.T, X)
            batch_offset = (self.mean_ - batch_mean)
            batch_adjustment = np.dot(batch_offset[None].T, batch_offset[None])
            batch_covar += batch_adjustment * n_samples

            mean_offset = (self.mean_ - prev_mean)
            mean_adjustment = np.dot(mean_offset[None].T, mean_offset[None])
            self.covar_ += mean_adjustment * prev_sample_count

            self.covar_ += batch_covar
            self.n_samples_seen_ += n_samples

    def transform(self, X):
        if self.copy:
            X = np.array(X, copy=self.copy)
            X = np.copy(X)
        if self.components_ is None:
            U, S, VT = svd(self.covar_ / self.n_samples_seen_,
                           full_matrices=False)
            components = np.dot(VT.T * np.sqrt(1.0 / (S + self.bias)), VT)
            self.components_ = components[:self.n_components]
        X /= self.scale_by
        X -= self.mean_
        X_transformed = np.dot(X, self.components_.T)
        return X_transformed


class IncrementalZCA(BaseEstimator, TransformerMixin):
    def __init__(self, n_components=None, batch_size=None, bias=.1,
                 scale_by=1., copy=True):
        self.n_components = n_components
        self.batch_size = batch_size
        self.bias = bias
        self.scale_by = scale_by
        self.copy = copy
        self.scale_by = float(scale_by)
        self.n_samples_seen_ = 0.
        self.mean_ = None
        self.var_ = None
        self.components_ = None

    def fit(self, X, y=None):
        self.n_samples_seen_ = 0.
        self.mean_ = None
        self.var_ = None
        self.components_ = None
        n_samples, n_features = X.shape
        if self.batch_size is None:
            self.batch_size_ = 5 * n_features
        else:
            self.batch_size_ = self.batch_size
        for batch in gen_batches(n_samples, self.batch_size_):
            self.partial_fit(X[batch])
        return self

    def partial_fit(self, X):
        if self.copy:
            X = np.array(X, copy=self.copy)
            X = np.copy(X)
        n_samples, n_features = X.shape
        self.n_components_ = self.n_components
        X /= self.scale_by
        if self.components_ is None:
            # This is the first pass through partial_fit
            self.n_samples_seen_ = 0.
            col_var = X.var(axis=0)
            col_mean = X.mean(axis=0)
            X -= col_mean
            U, S, V = svd(X, full_matrices=False)
            U, V = svd_flip(U, V, u_based_decision=False)
        else:
            col_batch_mean = X.mean(axis=0)
            col_mean, col_var, n_total_samples = _batch_mean_variance_update(
                X, self.mean_, self.var_, self.n_samples_seen_)
            X -= col_batch_mean
            # Build matrix of combined previous basis and new data
            correction = np.sqrt((self.n_samples_seen_ * n_samples)
                                  / n_total_samples)
            mean_correction = correction * (self.mean_ - col_batch_mean)
            X_combined = np.vstack((self.singular_values_.reshape((-1, 1)) *
                                    self.components_,
                                    X,
                                    mean_correction))
            U, S, V = svd(X_combined, full_matrices=False)
            U, V = svd_flip(U, V, u_based_decision=False)

        self.n_samples_seen_ += n_samples
        self.components_ = V[:self.n_components_]
        self.singular_values_ = S[:self.n_components_]
        self.mean_ = col_mean
        self.var_ = col_var
        self.zca_components_ = np.dot(self.components_.T *
            np.sqrt(1.0 / (self.singular_values_ ** 2 + self.bias)), self.components_)

    def transform(self, X):
        if self.copy:
            X = np.array(X, copy=self.copy)
            X = np.copy(X)
        X /= self.scale_by
        X -= self.mean_
        X_transformed = np.dot(X, self.zca_components_.T)
        return X_transformed


if __name__ == "__main__":
    from numpy.testing import assert_almost_equal
    import matplotlib.pyplot as plt
    from scipy.misc import lena
    # scale_by is necessary otherwise float32 results are numerically unstable
    # scale_by is still not enough to totally eliminate the error in float32
    # for many, many iterations but it is very close
    X = lena().astype('float32')
    X_orig = np.copy(X)

    # Check that covariance ZCA and data ZCA produce same results
    czca = CovZCA()
    zca = ZCA()
    X_czca = czca.fit_transform(X)
    X_zca = zca.fit_transform(X)
    assert_almost_equal(abs(zca.components_), abs(czca.components_), 3)
    raise ValueError()


    random_state = np.random.RandomState(1999)
    X = random_state.rand(2000, 512).astype('float64') * 255.
    X_orig = np.copy(X)
    scale_by = 1.
    from sklearn.decomposition import PCA, IncrementalPCA
    zca = ZCA(n_components=512, scale_by=scale_by)
    pca = PCA(n_components=512)
    izca = IncrementalZCA(n_components=512, batch_size=1000)
    ipca = IncrementalPCA(n_components=512, batch_size=1000)
    X_pca = pca.fit_transform(X)
    X_zca = zca.fit_transform(X)
    X_izca = izca.fit_transform(X)
    X_ipca = ipca.fit_transform(X)
    assert_almost_equal(abs(pca.components_), abs(ipca.components_), 3)
    from IPython import embed; embed()
    assert_almost_equal(abs(zca.components_), abs(izca.zca_components_), 3)

    for batch_size in [512, 128]:
        print("Testing batch size %i" % batch_size)
        izca = IncrementalZCA(batch_size=batch_size, scale_by=scale_by)
        # Test that partial fit over subset has the same mean!
        zca.fit(X[:batch_size])
        izca.partial_fit(X[:batch_size])
        # Make sure data was not modified
        assert_almost_equal(X[:batch_size], X_orig[:batch_size])
        # Make sure single batch results match
        assert_almost_equal(zca.mean_, izca.mean_, decimal=3)
        print("Got here")

        izca.fit(X[:100])
        izca.partial_fit(X[100:200])
        zca.fit(X[:200])
        # Make sure 2 batch results match
        assert_almost_equal(zca.mean_, izca.mean_, decimal=3)
        print("Got here 2")
        # Make sure the input array is not modified
        assert_almost_equal(X, X_orig, decimal=3)
        X_zca = zca.fit_transform(X)
        X_izca = izca.fit_transform(X)
        # Make sure the input array is not modified
        assert_almost_equal(X, X_orig, decimal=3)
        print("Got here 3")
        # Make sure the means are equal
        assert_almost_equal(zca.mean_, izca.mean_, decimal=3)
        print("Got here 4")
        # Make sure the components are equal
        assert_almost_equal(X_zca, X_izca, decimal=3)
    plt.imshow(X, cmap="gray")
    plt.title("Original")
    plt.figure()
    plt.imshow(X_zca, cmap="gray")
    plt.title("ZCA")
    plt.figure()
    plt.imshow(X_izca, cmap="gray")
    plt.title("IZCA")
    plt.figure()
    plt.matshow(zca.components_)
    plt.title("ZCA")
    plt.figure()
    plt.matshow(izca.components_)
    plt.title("IZCA")
    plt.show()
