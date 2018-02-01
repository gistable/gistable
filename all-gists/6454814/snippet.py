from pyspark import SparkContext

import numpy as np

from sklearn.cross_validation import train_test_split, Bootstrap
from sklearn.datasets import make_classification
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier

def run(sc):
	def zero_matrix(n, m):
		return np.zeros(n*m, dtype = int).reshape(n, m)
	
	def vote_increment(y_est):
		increment = zero_matrix(y_est.size, n_ys)
		increment[np.arange(y_est.size), y_est] = 1
		return increment # test point x class matrix with 1s marking the estimator prediction

	X, y = make_classification()
	X_train, X_test, y_train, y_test = train_test_split(X, y)

	n_test = X_test.shape[0]
	n_ys = np.unique(y_train).size
	
	model = DecisionTreeClassifier()
	# Partition the training data into random sub-samples with replacement.
	samples = sc.parallelize(Bootstrap(y.size))
	# Train a model for each sub-sample and apply it to the test data.
	vote_tally = samples.map(lambda (index, _):
		model.fit(X[index], y[index]).predict(X_test)
	).map(vote_increment).fold(zero_matrix(n_test, n_ys), np.add) # Take the learner majority vote.
	y_estimate_vote = np.argmax(vote_tally, axis = 1)
	return accuracy_score(y_test, y_estimate_vote)

if __name__ == '__main__':
	print run(SparkContext("local", "Boost"))
