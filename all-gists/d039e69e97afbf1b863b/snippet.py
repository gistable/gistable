from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.cross_validation import cross_val_score
from jpjplearn.datasets import load_clf_corpus
from jpjplearn.analyzer import mecab_analyzer

# ../all/0/*.txt
#       /1/*.txt
X, y = load_clf_corpus("../all")

nb = Pipeline([('vec', TfidfVectorizer(analyzer=mecab_analyzer)), ('clf', MultinomialNB(alpha=0.05))])
#nb = Pipeline([('vec', HashingVectorizer(analyzer=mecab_analyzer, non_negative=True)), ('clf', MultinomialNB(alpha=0.05))])
svc = Pipeline([('vec', TfidfVectorizer(analyzer=mecab_analyzer)), ('clf', SVC(C=1.0, kernel='linear'))])
#svc = Pipeline([('vec', HashingVectorizer(analyzer=mecab_analyzer, non_negative=True)), ('clf', SVC(C=1.0, kernel='linear'))])
sgd = Pipeline([('vec', HashingVectorizer(analyzer=mecab_analyzer)), ('clf', SGDClassifier(n_iter=100, penalty='l2'))])

cross_val_score(nb, X, y, scoring='accuracy').mean()
cross_val_score(nb, X, y, scoring='precision').mean()
cross_val_score(nb, X, y, scoring='recall').mean()
cross_val_score(nb, X, y, scoring='f1').mean()

cross_val_score(svc, X, y, scoring='accuracy').mean()
cross_val_score(svc, X, y, scoring='precision').mean()
cross_val_score(svc, X, y, scoring='recall').mean()
cross_val_score(svc, X, y, scoring='f1').mean()
