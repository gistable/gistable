from __future__ import print_function

import json
import os
import numpy as np

from gensim.models import Word2Vec
from gensim.utils import simple_preprocess
from keras.engine import Input
from keras.layers import Embedding, merge
from keras.models import Model

# tokenizer: can change this as needed
tokenize = lambda x: simple_preprocess(x)


def create_embeddings(data_dir,
                      embeddings_path='embeddings.npz',
                      vocab_path='map.json',
                      **params):
    """
    Generate embeddings from a batch of text
    :param embeddings_path: where to save the embeddings
    :param vocab_path: where to save the word-index map
    """

    class SentenceGenerator(object):
        def __init__(self, dirname):
            self.dirname = dirname

        def __iter__(self):
            for fname in os.listdir(self.dirname):
                for line in open(os.path.join(self.dirname, fname)):
                    yield tokenize(line)

    sentences = SentenceGenerator(data_dir)

    model = Word2Vec(sentences, **params)
    weights = model.syn0
    np.save(open(embeddings_path, 'wb'), weights)

    vocab = dict([(k, v.index) for k, v in model.vocab.items()])
    with open(vocab_path, 'w') as f:
        f.write(json.dumps(vocab))


def load_vocab(vocab_path='map.json'):
    """
    Load word -> index and index -> word mappings
    :param vocab_path: where the word-index map is saved
    :return: word2idx, idx2word
    """

    with open(vocab_path, 'r') as f:
        data = json.loads(f.read())
    word2idx = data
    idx2word = dict([(v, k) for k, v in data.items()])
    return word2idx, idx2word


def word2vec_embedding_layer(embeddings_path='embeddings.npz'):
    """
    Generate an embedding layer word2vec embeddings
    :param embeddings_path: where the embeddings are saved (as a numpy file)
    :return: the generated embedding layer
    """
    
    weights = np.load(open(embeddings_path, 'rb'))
    layer = Embedding(input_dim=weights.shape[0],
                      output_dim=weights.shape[1],
                      weights=[weights])
    return layer

if __name__ == '__main__':
    # specify embeddings in this environment variable
    data_path = os.environ['EMBEDDINGS_TEXT_PATH']

    # variable arguments are passed to gensim's word2vec model
    create_embeddings(data_path, size=100, min_count=5,
                      window=5, sg=1, iter=25)

    word2idx, idx2word = load_vocab()

    # cosine similarity model
    input_a = Input(shape=(1,), dtype='int32', name='input_a')
    input_b = Input(shape=(1,), dtype='int32', name='input_b')
    embeddings = word2vec_embedding_layer()
    embedding_a = embeddings(input_a)
    embedding_b = embeddings(input_b)
    similarity = merge([embedding_a, embedding_b],
                       mode='cos', dot_axes=2)

    model = Model(input=[input_a, input_b], output=[similarity])
    model.compile(optimizer='sgd', loss='mse')
    
    while True:
        word_a = raw_input('First word: ')
        if word_a not in word2idx:
            print('Word "%s" is not in the index' % word_a)
            continue
        word_b = raw_input('Second word: ')
        if word_b not in word2idx:
            print('Word "%s" is not in the index' % word_b)
            continue
        output = model.predict([np.asarray([word2idx[word_a]]),
                                np.asarray([word2idx[word_b]])])
        print(output)
