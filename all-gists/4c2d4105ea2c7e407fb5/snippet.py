""" Messing around with scikit-learn.  """

import sys

import numpy as np
import scipy.sparse

import sklearn.linear_model
import sklearn.datasets
import sklearn.svm
import sklearn.metrics
import sklearn.decomposition
import sklearn.feature_extraction.text
import sklearn.utils.sparsefuncs

# The fetch_20newsgroups dataset uses logging that we need to setup.
import logging
logging.basicConfig()

# http://scikit-learn.org/stable/datasets/index.html#the-20-newsgroups-text-dataset
dataset = sklearn.datasets.fetch_20newsgroups(
    shuffle=True,
)
corpus = dataset.data
n_samples = len(corpus)
target = [[0] * n_samples] * n_samples
for i in range(n_samples):
    target[i][dataset.target[i]] = 1.0

print "* shape of the corpus", len(corpus)

print "Convert text data into numerical vectors"
# http://scikit-learn.org/stable/modules/feature_extraction.html
vectorizer = sklearn.feature_extraction.text.CountVectorizer(
    stop_words='english',
    ngram_range=(1, 1),  #ngram_range=(1, 1) is the default
    dtype='double',
)
data = vectorizer.fit_transform(corpus)
print "* shape of the tfidf vectors", data.shape

# Save this to compute explained variance later
vectors = data

print "Reduce the dimensionality of the data"
pca = sklearn.decomposition.TruncatedSVD(n_components=50)
data = pca.fit_transform(data)

print "* shape of the pca components", data.shape
exp = np.var(data, axis=0)
full = sklearn.utils.sparsefuncs.mean_variance_axis0(vectors)[1].sum()
explained_variance_ratios = exp / full
confidence = sum(explained_variance_ratios)

if confidence < 0.8:
    print "explained variance ratio %f < 0.8.  Bailing." % confidence
    sys.exit(1)

print "Training a support vector machine on first half"
regression = sklearn.linear_model.LinearRegression()
regression.fit(data[:n_samples / 2], target[:n_samples / 2])

print "Now predict the value of on the second half"
expected = target[n_samples / 2:]
predicted = regression.predict(data[n_samples / 2:])

print(
    "Regression report for regression %s:\n%s\n"
    % (regression, sklearn.metrics.mean_squared_error(expected, predicted)))