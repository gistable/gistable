import pandas as pd
from ggplot import *
from sklearn.datasets import fetch_20newsgroups
from sklearn.metrics import roc_curve

# vectorizer
from sklearn.feature_extraction.text import HashingVectorizer

# our classifiers
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier

categories = [
    'alt.atheism',
    'talk.religion.misc',
    'comp.graphics',
    'sci.space'
]

data_train = fetch_20newsgroups(subset='train', categories=categories,
        shuffle=True, random_state=42)

data_test = fetch_20newsgroups(subset='test', categories=categories,
        shuffle=True, random_state=42)

categories = data_train.target_names

vectorizer = HashingVectorizer(stop_words='english', non_negative=True, n_features=1000)
X_train = vectorizer.fit_transform(data_train.data)
X_test = vectorizer.transform(data_test.data)

y_train = data_train.target==0
y_test = data_test.target==0



clfs = [
    ("MultinomialNB", MultinomialNB()),
    ("BernoulliNB", BernoulliNB()),
    ("KNeighborsClassifier", KNeighborsClassifier()),
    ("RandomForestClassifier", RandomForestClassifier()),
    ("SVM", SVC(probability=True))
]

all_results = None
for name, clf in clfs:
    clf.fit(X_train.todense(), y_train)
    probs = clf.predict_proba(X_test.todense())[:,1]
    fpr, tpr, thresh = roc_curve(y_test, probs)
    results = pd.DataFrame({
        "name": name,
        "fpr": fpr,
        "tpr": tpr
    })
    if all_results is None:
        all_results = results
    else:
        all_results = all_results.append(results)

ggplot(aes(x='fpr', y='tpr', color='name'), data=all_results) + \
    geom_step() + \
    geom_abline(color="black") + \
    ggtitle("Text Classification Benchmark on 20 News Groups")

