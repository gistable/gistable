import numpy as np
import marisa_trie
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.externals import six

class MarisaCountVectorizer(CountVectorizer):

    # ``CountVectorizer.fit`` method calls ``fit_transform`` so
    # ``fit`` is not provided
    def fit_transform(self, raw_documents, y=None):
        X = super(MarisaCountVectorizer, self).fit_transform(raw_documents)
        X = self._freeze_vocabulary(X)
        return X

    def _freeze_vocabulary(self, X=None):
        if not self.fixed_vocabulary_:
            frozen = marisa_trie.Trie(six.iterkeys(self.vocabulary_))
            if X is not None:
                X = self._reorder_features(X, self.vocabulary_, frozen)
            self.vocabulary_ = frozen
            self.fixed_vocabulary_ = True
            del self.stop_words_
        return X

    def _reorder_features(self, X, old_vocabulary, new_vocabulary):
        map_index = np.empty(len(old_vocabulary), dtype=np.int32)
        for term, new_val in six.iteritems(new_vocabulary):
            map_index[new_val] = old_vocabulary[term]
        return X[:, map_index]
