# Keras==1.0.6
from keras.models import Sequential
import numpy as np
from keras.layers.recurrent import LSTM
from keras.layers.core import TimeDistributedDense, Activation
from keras.preprocessing.sequence import pad_sequences
from keras.layers.embeddings import Embedding
from sklearn.cross_validation import train_test_split
from keras.layers import Merge
from keras.backend import tf
from lambdawithmask import Lambda as MaskLambda
from sklearn.metrics import confusion_matrix, accuracy_score

raw = open('wikigold.conll.txt', 'r').readlines()
all_x = []
point = []
for line in raw:
    stripped_line = line.strip().split(' ')
    point.append(stripped_line)
    if line == '\n':
        all_x.append(point[:-1])
        point = []
all_x = all_x[:-1]
lengths = [len(x) for x in all_x]
short_x = [x for x in all_x if len(x) < 64]

X = [[c[0] for c in x] for x in short_x]
y = [[c[1] for c in y] for y in short_x]

all_text = [c for x in X for c in x]
words = list(set(all_text))
word2ind = {word: index for index, word in enumerate(words)}
ind2word = {index: word for index, word in enumerate(words)}
labels = list(set([c for x in y for c in x]))
label2ind = {label: (index + 1) for index, label in enumerate(labels)}
ind2label = {(index + 1): label for index, label in enumerate(labels)}
print 'Input sequence length range: ', max(lengths), min(lengths)

maxlen = max([len(x) for x in X])
print 'Maximum sequence length:', maxlen


def encode(x, n):
    result = np.zeros(n)
    result[x] = 1
    return result

X_enc = [[word2ind[c] for c in x] for x in X]
X_enc_reverse = [[c for c in reversed(x)] for x in X_enc]
max_label = max(label2ind.values()) + 1
y_enc = [[0] * (maxlen - len(ey)) + [label2ind[c] for c in ey] for ey in y]
y_enc = [[encode(c, max_label) for c in ey] for ey in y_enc]

X_enc_f = pad_sequences(X_enc, maxlen=maxlen)
X_enc_b = pad_sequences(X_enc_reverse, maxlen=maxlen)
y_enc = pad_sequences(y_enc, maxlen=maxlen)

(X_train_f, X_test_f, X_train_b,
 X_test_b, y_train, y_test) = train_test_split(X_enc_f, X_enc_b, y_enc,
                                               test_size=11*32, train_size=45*32, random_state=42)
print 'Training and testing tensor shapes:'
print X_train_f.shape, X_test_f.shape, X_train_b.shape, X_test_b.shape, y_train.shape, y_test.shape

max_features = len(word2ind)
embedding_size = 128
hidden_size = 32
out_size = len(label2ind) + 1


def reverse_func(x, mask=None):
    return tf.reverse(x, [False, True, False])


model_forward = Sequential()
model_forward.add(Embedding(max_features, embedding_size, input_length=maxlen, mask_zero=True))
model_forward.add(LSTM(hidden_size, return_sequences=True))  

model_backward = Sequential()
model_backward.add(Embedding(max_features, embedding_size, input_length=maxlen, mask_zero=True))
model_backward.add(LSTM(hidden_size, return_sequences=True))
model_backward.add(MaskLambda(function=reverse_func, mask_function=reverse_func))

model = Sequential()

model.add(Merge([model_forward, model_backward], mode='concat'))
model.add(TimeDistributedDense(out_size))
model.add(Activation('softmax'))

model.compile(loss='categorical_crossentropy', optimizer='adam')

batch_size = 32
model.fit([X_train_f, X_train_b], y_train, batch_size=batch_size, nb_epoch=40,
          validation_data=([X_test_f, X_test_b], y_test))
score = model.evaluate([X_test_f, X_test_b], y_test, batch_size=batch_size)
print('Raw test score:', score)


def score(yh, pr):
    coords = [np.where(yhh > 0)[0][0] for yhh in yh]
    yh = [yhh[co:] for yhh, co in zip(yh, coords)]
    ypr = [prr[co:] for prr, co in zip(pr, coords)]
    fyh = [c for row in yh for c in row]
    fpr = [c for row in ypr for c in row]
    return fyh, fpr

pr = model.predict_classes([X_train_f, X_train_b])
yh = y_train.argmax(2)
fyh, fpr = score(yh, pr)
print 'Training accuracy:', accuracy_score(fyh, fpr)
print 'Training confusion matrix:'
print confusion_matrix(fyh, fpr)

pr = model.predict_classes([X_test_f, X_test_b])
yh = y_test.argmax(2)
fyh, fpr = score(yh, pr)
print 'Testing accuracy:', accuracy_score(fyh, fpr)
print 'Testing confusion matrix:'
print confusion_matrix(fyh, fpr)
