#!/usr/bin/env python
# encoding: utf-8
import codecs
import os
import sys

import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer

def get_document_filenames(document_path='/home/tool/document_text'):
    return [os.path.join(document_path, each)
            for each in os.listdir(document_path)]


def create_vectorizer():
    # Arguments here are tweaked for working with a particular data set.
    # All that's really needed is the input argument.
    return TfidfVectorizer(input='filename', max_features=200,
                           token_pattern='(?u)\\b[a-zA-Z]\\w{2,}\\b',
                           max_df=0.05,
                           stop_words='english',
                           ngram_range=(1, 3))


def display_scores(vectorizer, tfidf_result):
    # http://stackoverflow.com/questions/16078015/
    scores = zip(vectorizer.get_feature_names(),
                 np.asarray(tfidf_result.sum(axis=0)).ravel())
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
    for item in sorted_scores:
        print "{0:50} Score: {1}".format(item[0], item[1])


def main():
    vectorizer = create_vectorizer()
    tfidf_result = vectorizer.fit_transform(get_document_filenames())
    display_scores(vectorizer, tfidf_result)

if __name__ == '__main__':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    main()