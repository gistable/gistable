from sklearn.base import BaseEstimator

def piper(self, other):
    from sklearn.pipeline import make_pipeline, Pipeline
    if isinstance(self, Pipeline):
        steps = ([estimator for (name, estimator) in self.steps] + [other])
        return make_pipeline(*steps)
    else:
        return make_pipeline(self, other)

def unionizer(self, other):
    from sklearn.pipeline import make_union, FeatureUnion
    if isinstance(self, FeatureUnion):
        steps = ([estimator for (name, estimator) in self.steps] + [other])
        return make_union(*steps)
    else:
        return make_union(self, other)

BaseEstimator.__rshift__ = piper
BaseEstimator.__mul__ = unionizer