'''This scripts implements Kim's paper "Convolutional Neural Networks for Sentence Classification"
with a very small embedding size (20) than the commonly used values (100 - 300) as it gives better
result with much less parameters.

Run on GPU: THEANO_FLAGS=mode=FAST_RUN,device=gpu,floatX=float32 python imdb_cnn.py

Get to 0.853 test accuracy after 5 epochs. 13s/epoch on Nvidia GTX980 GPU.
'''

from __future__ import print_function
import numpy as np
np.random.seed(1337)  # for reproducibility

from keras.preprocessing import sequence
from keras.models import Graph
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.embeddings import Embedding
from keras.layers.convolutional import Convolution1D, MaxPooling1D
from keras.datasets import imdb
from keras.utils.np_utils import accuracy

# set parameters:
max_features = 5000  # vocabulary size
maxlen = 100  # maximum length of the review
batch_size = 32
embedding_dims = 20
ngram_filters = [3, 5, 7]
nb_filter = 1200  # number of filters for each ngram_filter
nb_epoch = 5

# prepare data
print('Loading data...')
(X_train, y_train), (X_test, y_test) = imdb.load_data(nb_words=max_features,
                                                      test_split=0.2)
print(len(X_train), 'train sequences')
print(len(X_test), 'test sequences')

print('Pad sequences (samples x time)')
X_train = sequence.pad_sequences(X_train, maxlen=maxlen)
X_test = sequence.pad_sequences(X_test, maxlen=maxlen)
print('X_train shape:', X_train.shape)
print('X_test shape:', X_test.shape)

# define model
model = Graph()
model.add_input(name='input', input_shape=(maxlen,), dtype=int)
model.add_node(Embedding(max_features, embedding_dims, input_length=maxlen), name='embedding', input='input')
model.add_node(Dropout(0.), name='dropout_embedding', input='embedding')
for n_gram in ngram_filters:
    model.add_node(Convolution1D(nb_filter=nb_filter,
                                 filter_length=n_gram,
                                 border_mode='valid',
                                 activation='relu',
                                 subsample_length=1,
                                 input_dim=embedding_dims,
                                 input_length=maxlen),
                   name='conv_' + str(n_gram),
                   input='dropout_embedding')
    model.add_node(MaxPooling1D(pool_length=maxlen - n_gram + 1),
                   name='maxpool_' + str(n_gram),
                   input='conv_' + str(n_gram))
    model.add_node(Flatten(),
                   name='flat_' + str(n_gram),
                   input='maxpool_' + str(n_gram))
model.add_node(Dropout(0.), name='dropout', inputs=['flat_' + str(n) for n in ngram_filters])
model.add_node(Dense(1, input_dim=nb_filter * len(ngram_filters)), name='dense', input='dropout')
model.add_node(Activation('sigmoid'), name='sigmoid', input='dense')
model.add_output(name='output', input='sigmoid')
print(model.summary())

# train model
model.compile(loss={'output': 'binary_crossentropy'}, optimizer='rmsprop')
model.fit({'input': X_train, 'output': y_train},
          batch_size=batch_size,
          nb_epoch=nb_epoch,
          validation_data={'input': X_test, 'output': y_test})
acc = accuracy(y_test,
               np.round(np.array(model.predict({'input': X_test},
                                               batch_size=batch_size)['output'])))
print('Test accuracy:', acc)
