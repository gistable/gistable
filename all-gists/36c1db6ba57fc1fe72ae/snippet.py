from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import pandas as pd
import numpy as np

# Grab just two categories from the 20 newsgroups dataset
categories=['sci.space', 'rec.autos']

# Get training data
ngd = fetch_20newsgroups(subset='train', categories=categories)
X_train = ngd.data
y_train = ngd.target

# Use pipeline for easy extensibility
steps = [
	('vectorizer', TfidfVectorizer()),
	('classifier', LogisticRegression(penalty='l1', C=10))
]
pipeline = Pipeline(steps)

# Fit and assess training performance
pipeline.fit(X_train, y_train)
pred = pipeline.predict(X_train)
print("Classification accuracy on training data: %.2f" % pipeline.score(X_train, y_train))

# Performance on test data
ngd = fetch_20newsgroups(subset='test', categories=categories)
test_score = pipeline.score(ngd.data, ngd.target)
print("Classification accuracy on test data: %.2f" % test_score)

# Print largest coefficients
vec, clf = pipeline.named_steps['vectorizer'], pipeline.named_steps['classifier']
coefs = pd.Series(clf.coef_[0], index=vec.get_feature_names())
print("\n20 most discriminating words:")
print(coefs[coefs.abs().sort_values(ascending=False).index][:20])
