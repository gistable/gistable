import os
import random
import string
from subprocess import call

import numpy as np

from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.datasets import dump_svmlight_file


FESTPATH = "/home/tobias/applications/fest/"


def id_generator(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


class FEST(BaseEstimator, ClassifierMixin):
    """
    Simple Python Wrapper for FEST (https://github.com/fest/fest)
    Supports only binary classification.
    """

    def __init__(self):
        self.model = id_generator(10)

    def __del__(self):
        call(["rm", self.model_filename])

    def fit(self, X, y):
        self.train_filename = self.model + "_data.tmp"
        self.model_filename = self.model + "_model.tmp"

        with open(self.train_filename, 'wb') as f:
            dump_svmlight_file(X, y, f)

        call([os.path.join(FESTPATH, "festlearn"),
              "-c", "2",
              "-d", "1000",
              "-t", "100",
              self.train_filename, self.model_filename])

        call(["rm", self.train_filename])

    def predict_proba(self, X):
        self.test_filename = self.model + "_test.tmp"
        self.pred_filename = self.model + "_pred.tmp"

        y = np.array([-55] * X.shape[0])

        with open(self.test_filename, 'wb') as f:
            dump_svmlight_file(X, y, f)

        call([os.path.join(FESTPATH, "festclassify"), self.test_filename,
              self.model_filename, self.pred_filename])

        with open(self.pred_filename, 'rb') as f:
            y_pred = np.array([[-float(line), float(line)] for line in f])

        call(["rm", self.test_filename])
        call(["rm", self.pred_filename])

        return np.array(y_pred)

    def predict(self, X):
        return (self.predict_proba(X)[:,1] > 0).astype(int)
