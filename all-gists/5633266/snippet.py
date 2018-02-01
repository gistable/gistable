from collections import defaultdict
import re
import numpy as np

from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction import FeatureHasher
from sklearn.linear_model.stochastic_gradient import SGDClassifier
from sklearn.externals import joblib

def tokens(doc):
    """Extract tokens from doc.

    This uses a simple regex to break strings into tokens. For a more
    principled approach, see CountVectorizer or TfidfVectorizer.
    """
    return (tok.lower() for tok in re.findall(r"\w+", doc))

def token_freqs(doc):
    """Extract a dict mapping tokens from doc to their frequencies."""
    freq = defaultdict(int)
    for tok in tokens(doc):
        freq[tok] += 1
    return freq

def chunker(seq, size):
    """Iterate by chunks on a sequence. Here we simulate what reading
    from a stream would do by using a generator."""
    for pos in xrange(0, len(seq), size):
        yield seq[pos:pos + size]

categories = [
    'alt.atheism',
    'comp.graphics',
    'comp.sys.ibm.pc.hardware',
    'misc.forsale',
    'rec.autos',
    'sci.space',
    'talk.religion.misc',
]

dataset = fetch_20newsgroups(subset='train', categories=categories)
classif_data = zip(dataset.data, dataset.target)
classes = np.array(list(set(dataset.target)))

hasher = FeatureHasher()
classifier = SGDClassifier()

for i, chunk in enumerate(chunker(classif_data, 100)):
    messages, topics = zip(*chunk)
    X = hasher.transform(token_freqs(msg) for msg in messages)
    y = np.array(topics)
    classifier.partial_fit(X, 
                           topics,
                           classes=classes)
    if i % 100 == 0:
        # dump model to be able to monitor quality and later 
        # analyse convergence externally
        joblib.dump(classifier, 'model_%04d.pkl' % i)
