from sklearn.base import BaseEstimator,TransformerMixin

class LogTransformer(BaseEstimator,TransformerMixin):
    def __init__(self, constant=1, base='e'):
        from numpy import log,log10
        if base == 'e' or base == np.e:
            self.log = log
        elif base == '10' or base == 10:
            self.log = log10
        else:
            base_log = np.log(base)
            self.log = lambda x: np.log(x)/base_log
        self.constant = constant
        
    def fit(self, X, y=None):
        return self
    
    def transform(self, features):
        return self.log(features+self.constant)