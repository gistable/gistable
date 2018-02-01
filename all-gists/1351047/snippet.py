from sklearn.datasets import load_digits
from sklearn.svm import SVC
from sklearn.utils import shuffle
from sklearn.metrics import zero_one_score
import numpy as np


digits = load_digits()
X, y = shuffle(digits.data, digits.target)
X_train, X_test = X[:1000, :], X[1000:, :]
y_train, y_test = y[:1000], y[1000:]

svc = SVC(kernel='precomputed')

kernel_train = np.dot(X_train, X_train.T)  # linear kernel

svc.fit(kernel_train, y_train)

#kernel_test = np.dot(X_test, X_train[svc.support_, :].T)
kernel_test = np.dot(X_test, X_train.T)
y_pred = svc.predict(kernel_test)
print(zero_one_score(y_test, y_pred))

