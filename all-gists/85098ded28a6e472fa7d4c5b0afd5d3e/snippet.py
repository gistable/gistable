from __future__ import print_function

from keras import backend as K
from keras.engine import Input, Model, InputSpec
from keras.layers import Dense, Activation, Dropout, Lambda
from keras.layers import Embedding, LSTM
from keras.optimizers import Adam
from keras.preprocessing import sequence
from keras.utils.data_utils import get_file
from keras.datasets import imdb

import numpy as np
import random
import sys
import pdb

MAX_FEATURES = 20000
MAXLEN = 40
BATCH_SIZE = 32
STEP = 3
EMBEDDING_DIM = 32
RNN_HIDDEN_DIM = 32

# TODO: add normalization
# TODO: activation cluster?
# TODO: get forget gates from LSTMs (not sure how to grab temporary tensors inside loops)


def build_vocab():
    vocab = imdb.get_word_index()
    rev_vocab = {v: k for k, v in vocab.iteritems()}
    return vocab, rev_vocab


def vectorize(text, vocab, 
              maxlen=MAXLEN, start_char=1, oov_char=2, index_from=3):
    """ might not be consistent with vectorize_data. """
    if isinstance(text, basestring):
        text = [text]
    v = [[vocab.get(w, oov_char) for w in t.lower().split()] for t in text]
    return sequence.pad_sequences(v, maxlen=maxlen)


def vectorize_data(max_features=MAX_FEATURES, maxlen=MAXLEN, batch_size=BATCH_SIZE, limit=None):

    print('Loading data...')
    (X_train, y_train), (X_test, y_test) = imdb.load_data(nb_words=max_features)
    print(len(X_train), 'train sequences')
    print(len(X_test), 'test sequences')

    print('Pad sequences (samples x time)')
    X_train = sequence.pad_sequences(X_train, maxlen=maxlen)
    X_test = sequence.pad_sequences(X_test, maxlen=maxlen)
    print('X_train shape:', X_train.shape)
    print('X_test shape:', X_test.shape)

    if limit is None:
        return X_train, y_train, X_test, y_test
    else:
        return X_train[:limit], y_train[:limit], X_test[:limit], y_test[:limit]


def build_model(vocab_size, maxlen=MAXLEN, rnn_hidden_dim=RNN_HIDDEN_DIM):
    input_layer = Input(shape=(maxlen, ), name='input_layer', dtype='int32')
    embedding_layer = Embedding(vocab_size, EMBEDDING_DIM, input_length=maxlen, trainable=True, mask_zero=False, name='embedding_layer')(input_layer)  # -- ideally mask_zero=False but can't work with lambda layers
    recurrent_layer = LSTM(output_dim=rnn_hidden_dim, activation='tanh', return_sequences=True, name='recurrent_layer')(embedding_layer)
    last_step_layer = Lambda(lambda x: x[:, -1, :], output_shape=(rnn_hidden_dim, ), name='last_step_layer')(recurrent_layer)  # only needed for visualization
    output_layer = Dense(1, activation='sigmoid', name='output_layer')(last_step_layer)

    optimizer = Adam(lr=0.001)
    model = Model(input=input_layer, output=output_layer)
    print('Compiling...')
    model.compile(loss='binary_crossentropy', optimizer=optimizer)

    model.summary()
    return model


def visualize_model(model, include_gradients=False):
    recurrent_layer = model.get_layer('recurrent_layer')
    output_layer = model.get_layer('output_layer')

    inputs = []
    inputs.extend(model.inputs)

    outputs = []
    outputs.extend(model.outputs)
    outputs.append(recurrent_layer.output)
    outputs.append(recurrent_layer.W_f)  # -- weights of the forget gates (assuming LSTM)

    if include_gradients:
        loss = K.mean(model.output)  # [batch_size, 1] -> scalar
        grads = K.gradients(loss, recurrent_layer.output)
        grads_norm = grads / (K.sqrt(K.mean(K.square(grads))) + 1e-5)
        outputs.append(grads_norm)

    all_function = K.function(inputs, outputs)
    output_function = K.function([output_layer.input], model.outputs)
    return all_function, output_function


def get_compare_embeddings(original_embeddings, tuned_embeddings, vocab, dimreduce_type="pca", random_state=0):
    """ Compare embeddings drift. """
    if dimreduce_type == "pca":
        from sklearn.decomposition import PCA
        dimreducer = PCA(n_components=2, random_state=random_state)
    elif dimreduce_type == "tsne":
        from sklearn.manifold import TSNE
        dimreducer = TSNE(n_components=2, random_state=random_state)
    else:
        raise Exception("Wrong dimreduce_type.")

    reduced_original = dimreducer.fit_transform(original_embeddings)
    reduced_tuned = dimreducer.fit_transform(tuned_embeddings)

    def compare_embeddings(word):
        if word not in vocab:
            return None
        word_id = vocab[word]
        original_x, original_y = reduced_original[word_id, :]
        tuned_x, tuned_y = reduced_tuned[word_id, :]
        return original_x, original_y, tuned_x, tuned_y

    return compare_embeddings


if __name__ == '__main__':
    # -- train
    vocab, rev_vocab = build_vocab()
    X_train, y_train, X_test, y_test = vectorize_data(limit=1000)
    model = build_model(len(vocab))
    model.fit(X_train, y_train, batch_size=BATCH_SIZE, nb_epoch=1, verbose=True, # validation_split=0.05)
              validation_data=(X_test, y_test))

    acc = model.evaluate(X_test, y_test, batch_size=BATCH_SIZE)
    print('Test accuracy:', acc)

    # -- predict
    all_function, output_function = visualize_model(model, include_gradients=True)

    t = "HOW COULD anything originate out of its opposite?".lower()
    X = vectorize(t, vocab)
    
    # -- Return scores, raw rnn values and gradients
    # scores is equivalent to model.predict(X)
    scores, rnn_values, rnn_gradients, W_i = all_function([X])
    print(scores.shape, rnn_values.shape, rnn_gradients.shape, W_i.shape)

    # -- score prediction
    print("Scores:", scores)

    # -- Return scores at each step in the time sequence
    time_distributed_scores = map(lambda x: output_function([x]), rnn_values)
    print("Time distributed (word-level) scores:", map(lambda x: x[0], time_distributed_scores))

    pdb.set_trace()

    # -- if you have original embeddings, use here
    embeddings = model.get_weights()[0]
    compare_embeddings = get_compare_embeddings(embeddings, embeddings, vocab, dimreduce_type="pca", random_state=0)
    print("Embeddings drift:", compare_embeddings('d'))

