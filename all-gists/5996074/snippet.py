from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.metrics.pairwise import rbf_kernel


class KMeansTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, centroids):
        self.centroids = centroids

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        return rbf_kernel(X, self.centroids)