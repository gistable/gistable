# -*- coding: utf-8 -*-
"""
Improving approximate nearest neighbour search with k-nearest neigbors.
Using sklearn-KDTree here just for demonstration. You can plugin much faster
nearest neigbour search implementations (flann, annoy to name a few) for 
better results. For benchmarks, check out:
1) Radim Řehůřek (author of gensim) -
    http://rare-technologies.com/performance-shootout-of-nearest-neighbours-intro
2) Erik Bernhardsson (author of annoy) - 
    https://github.com/erikbern/ann-benchmarks
"""

import time, random
import numpy as np
from gensim.models import word2vec
from sklearn.neighbors import KDTree

# Download text8 dataset from:
# http://mattmahoney.net/dc/text8.zip
# and unzip the file

sentences = word2vec.Text8Corpus('text8')
model = word2vec.Word2Vec(sentences, size=200, workers=8)
model.init_sims(replace=True)    # normalize the vectors

words = random.sample(model.vocab.keys(),100)

class ANNSearch:
    word2idx = {}
    idx2word = {}
    data = []

    def __init__(self, model):
        for counter, key in enumerate(model.vocab.keys()):
            self.data.append(model[key])
            self.word2idx[key] = counter
            self.idx2word[counter] = key

        # leaf_size is a hyperparameter
        self.data = np.array(self.data)
        self.tree = KDTree(self.data, leaf_size=100)
        
    def search_by_vector(self, v, k=10):
        dists, inds = self.tree.query([v], k)
        return zip(dists[0], [self.idx2word[idx] for idx in inds[0]])

    def search(self, query, k=10):
        vector = self.data[self.word2idx[query]]
        return self.search_by_vector(vector, k)

# Linear Search
start = time.time()
for word in words:
    model.most_similar(word, topn=10)
stop = time.time()
print("time/query by (gensim's) Linear Search = %.2f ms" % (1000*float(stop-start)/len(words)))

# KDTree Search
search_model = ANNSearch(model)

start = time.time()
for word in words:
    search_model.search(word, k=10)
stop = time.time()
print("time/query by KDTree Search = %.2f ms" % (1000*float(stop-start)/len(words)))