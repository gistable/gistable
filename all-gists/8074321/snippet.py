from sklearn.base import BaseEstimator, TransformerMixin

class Transformer(BaseEstimator, TransformerMixin):
    def __init__(self, fn):
        self.fn = fn

    def fit(self, X, y):
        return self

    def transform(self, X):
        return self.fn(X)


if __name__ == '__main__':
    from sklearn import datasets, svm, pipeline, cross_validation
    iris = datasets.load_iris()
    p = pipeline.Pipeline([
        ('t', Transformer(svm.LinearSVC().fit(iris.data, iris.target).decision_function)),
        ('c', svm.LinearSVC()),
    ])
    print(cross_validation.cross_val_score(p, iris.data, iris.target))
    
