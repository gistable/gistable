# summarize
# Uses TFIDF to extract relevent sentences from text.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sun Oct 26 16:06:36 2014 -0400
#
# ID: summarize.py [] benjamin@bengfort.com $

"""
Uses TFIDF to extract relevent sentences from text.

Based off of Charlie Greenbacker's example from "A smattering of NLP with
Python" presentation he gave a while ago.
"""

##########################################################################
## Imports
##########################################################################

from __future__ import division

import re
import sys
import math
import nltk
import time
import random

from operator import itemgetter
from sklearn.feature_extraction.text import TfidfVectorizer

##########################################################################
## Module Fixtures
##########################################################################

lemmatizer = nltk.stem.WordNetLemmatizer()
stopwords  = set(nltk.corpus.stopwords.words('english'))

def timeit(func):
    def wrapper(*args, **kwargs):
        start  = time.time()
        result = func(*args, **kwargs)
        finit  = time.time()
        return result, finit-start
    return wrapper

def tokenize(text):
    for token in nltk.word_tokenize(text):
        token = token.lower()
        if token in stopwords or not token.isalpha():
            continue
        yield lemmatizer.lemmatize(token)

class TfidfSummarizer(object):

    def __init__(self, corpus, verbose=2):
        self.corpus     = corpus
        self.tokenizer  = tokenize
        self.vectorizer = TfidfVectorizer(tokenizer=self.tokenizer, decode_error='ignore')
        self.tdm        = None
        self.features   = None

        self.initialize_features(verbose)

    def initialize_features(self, verbose=1):
        """
        Initializes the features and prints time taken if verbose > 0.
        """

        @timeit
        def inner(self):
            # articles = dict((fileid, self.corpus.raw(fileid)) for fileid in self.corpus.fileids())
            return self.vectorizer.fit_transform(self.corpus.raw(fileid) for fileid in self.corpus.fileids())

        self.tdm, delta = inner(self)
        self.features  = self.vectorizer.get_feature_names()

        if verbose > 0:
            print "TDM contains %i terms and %i documents." % (len(self.features), self.tdm.shape[0])

        if verbose > 1:
            print "   First term:   %s" % self.features[0]
            print "   Last term:    %s" % self.features[-1]

            for idx in xrange(0, 4):
                print "   Random term:  %s" % random.choice(self.features[1:-2])

        if verbose > 0:
            print "Featurization took %0.3f seconds\n" % delta

    def score_sentences(self, fileid):
        fileidx = self.corpus.fileids().index(fileid)
        for sent in nltk.sent_tokenize(self.corpus.raw(fileid)):
            score  = 0
            for token in self.tokenizer(sent):
                if token not in self.features: continue
                score += self.tdm[fileidx, self.features.index(token)]
            yield score, sent

    def summarize(self, fileid):
        """
        Returns a summary for the given fileid
        """
        scores = list(self.score_sentences(fileid))
        sumlen = int(math.ceil(len(scores) / 2 ))
        scores.sort(key=itemgetter(0))

        return scores[:sumlen]

if __name__ == '__main__':
    summarizer = TfidfSummarizer(nltk.corpus.reuters)
    article = random.choice(nltk.corpus.reuters.fileids())

    print "#"*75
    print "## SUMMARY"
    print "#"*75
    print

    for sent in summarizer.summarize(article):
        print sent[1]

    print
    print "#"*75
    print "## ORIGINAL"
    print "#"*75
    print nltk.corpus.reuters.raw(article)
    print

