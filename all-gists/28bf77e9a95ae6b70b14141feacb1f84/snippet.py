from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.model_selection import cross_val_predict
from sklearn.pipeline import make_union
from sklearn.model_selection._split import check_cv
from sklearn.utils.validation import check_X_y

class BlendedClassifierTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, clf, cv=3):
        self.clf = clf
        self.cv = cv

    def fit(self, *args, **kwargs):
        self.clf = self.clf.fit(*args, **kwargs)
        return self

    def transform(self, *args, **kwargs):
        return self.clf.predict_proba(*args, **kwargs)

    def fit_transform(self, X, y):
        preds = cross_val_predict(self.clf, X, y, cv=self.cv, method='predict_proba')

        self.clf.fit(X, y)

        return preds


def make_stack_layer(*clfs):
    """
    Wrap around make_union that just wraps every class with
    `BlendedClassifierTransformer`
    """
    return make_union(*[BlendedClassifierTransformer(clf) for clf in clfs])

# Example usage:
from sklearn.pipeline import make_pipeline
from stacking import make_stack_layer
stack_layer = make_stack_layer(RandomForest(),
                               LinearSVM())
clf = make_pipeline(stack_layer, LogisticRegression())
# then the model can be used just like a regular model
clf.fit(Xtrain,ytrain)
clf.predict_proba(Xtest)