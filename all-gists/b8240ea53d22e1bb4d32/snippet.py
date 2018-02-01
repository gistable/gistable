# coding: utf-8

import sys
import jieba
import numpy
from sklearn import metrics
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.naive_bayes import MultinomialNB


def input_data(train_file, test_file):
    train_words = []
    train_tags = []
    test_words = []
    test_tags = []
    with open(train_file, 'r') as f1:
        for line in f1:
            tks = line.split('\t', 1)
            train_words.append(tks[1])
            train_tags.append(tks[0])
    with open(test_file, 'r') as f1:
        for line in f1:
            tks = line.split('\t', 1)
            test_words.append(tks[1])
            test_tags.append(tks[0])
    return train_words, train_tags, test_words, test_tags


with open('stopwords.txt', 'r') as f:
    stopwords = set([w.strip() for w in f])
comma_tokenizer = lambda x: jieba.cut(x, cut_all=True)


def vectorize(train_words, test_words):
    v = HashingVectorizer(tokenizer=comma_tokenizer, n_features=30000, non_negative=True)
    train_data = v.fit_transform(train_words)
    test_data = v.fit_transform(test_words)
    return train_data, test_data


def evaluate(actual, pred):
    m_precision = metrics.precision_score(actual, pred)
    m_recall = metrics.recall_score(actual, pred)
    print 'precision:{0:.3f}'.format(m_precision)
    print 'recall:{0:0.3f}'.format(m_recall)


def train_clf(train_data, train_tags):
    clf = MultinomialNB(alpha=0.01)
    clf.fit(train_data, numpy.asarray(train_tags))
    return clf


def main():
    if len(sys.argv) < 3:
        print '[Usage]: python classifier.py train_file test_file'
        sys.exit(0)
    train_file = sys.argv[1]
    test_file = sys.argv[2]
    train_words, train_tags, test_words, test_tags = input_data(train_file, test_file)
    train_data, test_data = vectorize(train_words, test_words)
    clf = train_clf(train_data, train_tags)
    pred = clf.predict(test_data)
    evaluate(numpy.asarray(test_tags), pred)


if __name__ == '__main__':
    main()