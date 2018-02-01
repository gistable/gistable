#!/usr/bin/env python
from __future__ import print_function
from keras.models import Sequential
from keras.layers import TimeDistributed
from keras.layers.core import Dense, Activation, Dropout, RepeatVector, TimeDistributedDense
from keras.layers.recurrent import LSTM
from keras.utils.data_utils import get_file
import numpy as np
import random,string
import sys

path = get_file('nietzsche.txt', origin="https://s3.amazonaws.com/text-datasets/nietzsche.txt")

try: 
    text = open(path).read().lower()
except UnicodeDecodeError:
    import codecs
    text = codecs.open(path, encoding='utf-8').read().lower()

print('corpus length:', len(text))

chars = set(text)
print('total chars:', len(chars))
char_indices = dict((c, i) for i, c in enumerate(chars))
indices_char = dict((i, c) for i, c in enumerate(chars))

maxlen = 4 # might be much easier with 3 or 2...
nbatch = 32

print('Vectorization...')
X = np.zeros((len(text), len(chars)), dtype=np.bool)
for t, char in enumerate(text):
    X[t, char_indices[char]] = 1


# build the model: 2 stacked LSTM
print('Build model...')
model = Sequential()
model.add(LSTM(512, stateful=True, return_sequences=False, batch_input_shape=(nbatch, maxlen, len(chars))))
model.add(Dense(256, activation='relu'))
model.add(RepeatVector(maxlen))
model.add(LSTM(512, stateful=True, return_sequences=True))
model.add(TimeDistributed(Dense(len(chars))))
model.add(Activation('softmax'))

model.compile(loss='categorical_crossentropy', optimizer='adam')


def sample(a, temperature=1.0):
    # helper function to sample an index from a probability array
    a = np.log(a) / temperature
    a = np.exp(a) / np.sum(np.exp(a))
    return np.argmax(np.random.multinomial(1, a, 1))

# start with a small sample that increases each iteration
numsamps = len(X)/100
numsampinc = len(X)/100

# train the model, output generated text after each iteration
for iteration in range(1, 100):
    print()
    print('-' * 50)
    print('Iteration', iteration)

    # get consecutive sequences for each "lane" by breaking the dataset
    # into 'nbatch' regions
    # X[0] X[s] X[2*s] ... X[(nbatch-1)*s] X[1] X[s+1] X[2*s+1] ...
    numsamps = min(len(X), numsamps)
    numsamps += numsampinc

    stride = int((numsamps-maxlen)/nbatch)
    sampsperbatch = int(stride/maxlen)
    totalsamps = sampsperbatch*nbatch
    XXs = np.zeros((totalsamps, maxlen, len(chars)), dtype=np.bool)
    YYs = np.zeros((totalsamps, maxlen, len(chars)), dtype=np.bool)
    for i in range(0,sampsperbatch):
      for j in range(0,nbatch):
        ofs = j*stride+i*maxlen
        XX = X[ofs:ofs+maxlen]
        YY = X[ofs+maxlen:ofs+maxlen*2]
        XXs[i*nbatch+j] = XX
        YYs[i*nbatch+j] = YY
    
    model.reset_states()
    model.fit(XXs, YYs, batch_size=nbatch, nb_epoch=3, shuffle=False)

    start_index = random.randint(0, len(text) - maxlen - 1)

    for diversity in [0.2, 0.5, 1.0, 1.2]:
        print()
        print('----- diversity:', diversity)

        generated = ''
        sentence = text[start_index: start_index + maxlen]
        generated += sentence
        print('----- Generating with seed: "' + sentence + '"')
        sys.stdout.write(generated)

        model.reset_states()
        for i in range(400/maxlen):
            x = np.zeros((nbatch, maxlen, len(chars)))
            for t, char in enumerate(sentence):
                x[0, t, char_indices[char]] = 1.

            # just get prediction from 1st batch
            preds_seq = model.predict(x, verbose=0)[0]
            
            # don't know if this is correct since each successive sample
            # doesn't take into account the prior...
            next_indices = [sample(preds, diversity) for preds in preds_seq]
            next_chars = string.join([indices_char[next_index] for next_index in next_indices],'')

            generated += next_chars
            sentence = next_chars

            sys.stdout.write(next_chars)
            sys.stdout.flush()
        print()
