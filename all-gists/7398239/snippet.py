#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import codecs
import numpy as np
import MeCab

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer

FILENAME = 'tweets.csv'
NUM_CLUSTERS = 1000
LSA_DIM = 500
MAX_DF = 0.8
MAX_FEATURES = 10000
MINIBATCH = True

def get_tweets_from_csv(filename):
    ret = csv.reader(open(filename))
    tweets = [r[7].decode('utf-8') for r in ret]

    for tweet in tweets[:]:
        if u'@' in tweet:
            tweets.remove(tweet)
        if len(tweet) <= 3:
            tweets.remove(tweet)
    return tweets


def analyzer(text):
    ret = []
    tagger = MeCab.Tagger('-Ochasen')
    node = tagger.parseToNode(text.encode('utf-8'))
    node = node.next
    while node.next:
        ret.append(node.feature.split(',')[-3].decode('utf-8'))
        node = node.next

    return ret


def main(filename):
    # load tweets
    tweets = get_tweets_from_csv(filename)

    # feature extraction
    vectorizer = TfidfVectorizer(analyzer=analyzer, max_df=MAX_DF)
    vectorizer.max_features = MAX_FEATURES
    X = vectorizer.fit_transform(tweets)

    # dimensionality reduction by LSA
    lsa = TruncatedSVD(LSA_DIM)
    X = lsa.fit_transform(X)
    X = Normalizer(copy=False).fit_transform(X)

    # clustering by KMeans
    if MINIBATCH:
        km = MiniBatchKMeans(n_clusters=NUM_CLUSTERS, init='k-means++', batch_size=1000, n_init=10, max_no_improvement=10, verbose=True)
    else:
        km = KMeans(n_clusters=NUM_CLUSTERS, init='k-means++', n_init=1, verbose=True)
    km.fit(X)
    labels = km.labels_

    transformed = km.transform(X)
    dists = np.zeros(labels.shape)
    for i in range(len(labels)):
        dists[i] = transformed[i, labels[i]]

    # sort by distance
    clusters = []
    for i in range(NUM_CLUSTERS):
        cluster = []
        ii = np.where(labels==i)[0]
        dd = dists[ii]
        di = np.vstack([dd,ii]).transpose().tolist()
        di.sort()
        for d, j in di:
            cluster.append(tweets[int(j)])
        clusters.append(cluster)

    return clusters


if __name__ == '__main__':
    clusters = main(FILENAME)
    f = codecs.open('%s.txt' % FILENAME, 'w', 'utf-8')
    for i,tweets in enumerate(clusters):
        for tweet in tweets:
            f.write('%d: %s\n' % (i, tweet.replace('/n', '')))
    f.close()