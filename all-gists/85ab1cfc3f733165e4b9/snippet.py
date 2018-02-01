# -*- coding: utf-8 -*-


import gensim
from sklearn.feature_extraction.text import CountVectorizer
from gensim.corpora.dictionary import Dictionary
from gensim.corpora import MmCorpus
import numpy as np
import lda

__author__ = 'satomacoto'

documents = ["Human machine interface for lab abc computer applications",
             "A survey of user opinion of computer system response time",
             "The EPS user interface management system",
             "System and human system engineering testing of EPS",
             "Relation of user perceived response time to error measurement",
             "The generation of random binary unordered trees",
             "The intersection graph of paths in trees",
             "Graph minors IV Widths of trees and well quasi ordering",
             "Graph minors A survey"]

# gensim
texts = [[word for word in document.lower().split()] for document in documents]
dictionary = Dictionary(texts)
dictionary.save('/tmp/deerwester.dict')
print(dictionary)
print(dictionary.token2id)
new_doc = "Human computer interaction"
new_vec = dictionary.doc2bow(new_doc.lower().split())
print(new_vec)
corpus = [dictionary.doc2bow(text) for text in texts]
print(corpus)
MmCorpus.serialize('/tmp/corpus.mm', corpus)
corpus = MmCorpus('/tmp/corpus.mm')
print(corpus)
print(list(corpus))

# sklearn
vec = CountVectorizer(min_df=1, stop_words=None, vocabulary=dictionary.token2id)
X = vec.fit_transform(documents)
vocab = vec.get_feature_names()

id2word = dict([(i, s) for i, s in enumerate(vec.get_feature_names())])
vocabulary = dictionary.token2id

print(X)
# CountVectorizer <-> corpus + Dictionary
print(gensim.matutils.Sparse2Corpus(X))
print(id2word)