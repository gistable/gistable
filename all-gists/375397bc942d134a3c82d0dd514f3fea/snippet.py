# Keras==1.0.6
import numpy as np
from keras.models import Sequential
from keras.layers.recurrent import LSTM
from keras.layers.core import TimeDistributedDense, Activation
from keras.preprocessing.sequence import pad_sequences
from keras.layers.embeddings import Embedding
from sklearn.cross_validation import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score, precision_recall_fscore_support

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
print 'Input sequence length range: ', max(lengths), min(lengths)

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
print 'Vocabulary size:', len(word2ind), len(label2ind)

maxlen = max([len(x) for x in X])
print 'Maximum sequence length:', maxlen


def encode(x, n):
    result = np.zeros(n)
    result[x] = 1
    return result

X_enc = [[word2ind[c] for c in x] for x in X]
max_label = max(label2ind.values()) + 1
y_enc = [[0] * (maxlen - len(ey)) + [label2ind[c] for c in ey] for ey in y]
y_enc = [[encode(c, max_label) for c in ey] for ey in y_enc]

X_enc = pad_sequences(X_enc, maxlen=maxlen)
y_enc = pad_sequences(y_enc, maxlen=maxlen)

X_train, X_test, y_train, y_test = train_test_split(X_enc, y_enc, test_size=11*32, train_size=45*32, random_state=42)
print 'Training and testing tensor shapes:', X_train.shape, X_test.shape, y_train.shape, y_test.shape

max_features = len(word2ind)
embedding_size = 128
hidden_size = 32
out_size = len(label2ind) + 1

model = Sequential()
model.add(Embedding(max_features, embedding_size, input_length=maxlen, mask_zero=True))
model.add(LSTM(hidden_size, return_sequences=True))  
model.add(TimeDistributedDense(out_size))
model.add(Activation('softmax'))

model.compile(loss='categorical_crossentropy', optimizer='adam')

batch_size = 32
model.fit(X_train, y_train, batch_size=batch_size, nb_epoch=10, validation_data=(X_test, y_test))
score = model.evaluate(X_test, y_test, batch_size=batch_size)
print('Raw test score:', score)


def score(yh, pr):
    coords = [np.where(yhh > 0)[0][0] for yhh in yh]
    yh = [yhh[co:] for yhh, co in zip(yh, coords)]
    ypr = [prr[co:] for prr, co in zip(pr, coords)]
    fyh = [c for row in yh for c in row]
    fpr = [c for row in ypr for c in row]
    return fyh, fpr

pr = model.predict_classes(X_train)
yh = y_train.argmax(2)
fyh, fpr = score(yh, pr)
print 'Training accuracy:', accuracy_score(fyh, fpr)
print 'Training confusion matrix:'
print confusion_matrix(fyh, fpr)
precision_recall_fscore_support(fyh, fpr)

pr = model.predict_classes(X_test)
yh = y_test.argmax(2)
fyh, fpr = score(yh, pr)
print 'Testing accuracy:', accuracy_score(fyh, fpr)
print 'Testing confusion matrix:'
print confusion_matrix(fyh, fpr)
precision_recall_fscore_support(fyh, fpr)
