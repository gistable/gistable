#!/usr/bin/python
# -*- coding: utf8 -*-

# SAMPLE SUBMISSION TO THE BIG DATA HACKATHON 13-14 April 2013 'Influencers in a Social Network'
# .... more info on Kaggle and links to go here
#
# written by Ferenc Huszár, PeerIndex

from sklearn import linear_model
from sklearn.metrics import auc_score
import numpy as np

###########################
# LOADING TRAINING DATA
###########################

trainfile = open('train.csv')
header = trainfile.next().rstrip().split(',')

y_train = []
X_train_A = []
X_train_B = []

for line in trainfile:
    splitted = line.rstrip().split(',')
    label = int(splitted[0])
    A_features = [float(item) for item in splitted[1:12]]
    B_features = [float(item) for item in splitted[12:]]
    y_train.append(label)
    X_train_A.append(A_features)
    X_train_B.append(B_features)
trainfile.close()

y_train = np.array(y_train)
X_train_A = np.array(X_train_A)
X_train_B = np.array(X_train_B)

###########################
# EXAMPLE BASELINE SOLUTION USING SCIKIT-LEARN
#
# using scikit-learn LogisticRegression module without fitting intercept
# to make it more interesting instead of using the raw features we transform them logarithmically
# the input to the classifier will be the difference between transformed features of A and B
# the method roughly follows this procedure, except that we already start with pairwise data
# http://fseoane.net/blog/2012/learning-to-rank-with-scikit-learn-the-pairwise-transform/
###########################

def transform_features(x):
    return np.log(1+x)

X_train = transform_features(X_train_A) - transform_features(X_train_B)
model = linear_model.LogisticRegression(fit_intercept=False)
model.fit(X_train,y_train)
# compute AuC score on the training data (BTW this is kind of useless due to overfitting, but hey, this is only an example solution)
p_train = model.predict_proba(X_train)
p_train = p_train[:,1:2]
print 'AuC score on training data:',auc_score(y_train,p_train.T)

###########################
# READING TEST DATA
###########################

testfile = open('test.csv')
#ignore the test header
testfile.next()

X_test_A = []
X_test_B = []
for line in testfile:
    splitted = line.rstrip().split(',')
    A_features = [float(item) for item in splitted[0:11]]
    B_features = [float(item) for item in splitted[11:]]
    X_test_A.append(A_features)
    X_test_B.append(B_features)
testfile.close()

X_test_A = np.array(X_test_A)
X_test_B = np.array(X_test_B)

# transform features in the same way as for training to ensure consistency
X_test = transform_features(X_test_A) - transform_features(X_test_B)
# compute probabilistic predictions
p_test = model.predict_proba(X_test)
#only need the probability of the 1 class
p_test = p_test[:,1:2]

###########################
# WRITING SUBMISSION FILE
###########################
predfile = open('predictions.csv','w+')

print >>predfile,','.join(header)
for line in np.concatenate((p_test,X_test_A,X_test_B),axis=1):
    print >>predfile, ','.join([str(item) for item in line])

predfile.close()