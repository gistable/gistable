from sklearn.cross_validation import train_test_split
from keras.preprocessing import sequence, text
from keras.models import Sequential
from keras.layers import (Dense, Dropout, Activation, Embedding, LSTM,
                            Convolution1D, MaxPooling1D)

# Embedding
max_features = 20000
maxlen = 100
embedding_size = 32

# Convolution
filter_length = 5
nb_filter = 64
pool_length = 4

# LSTM
lstm_output_size = 100

# Training
batch_size = 100
nb_epoch = 3

X = [x[1] for x in labeled_sample]
y = [x[0] for x in labeled_sample]

tk = text.Tokenizer(nb_words=2000, filters=text.base_filter(), 
                        lower=True, split=" ")
tk.fit_on_texts(X)
X = tk.texts_to_sequences(X)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, 
                                                    random_state=42)
X_train = sequence.pad_sequences(X_train, maxlen=maxlen)
X_test = sequence.pad_sequences(X_test, maxlen=maxlen)

model = Sequential()
model.add(Embedding(max_features, embedding_size, input_length=maxlen))
model.add(Dropout(0.4))
model.add(Convolution1D(nb_filter=nb_filter,
                        filter_length=filter_length,
                        border_mode='valid',
                        activation='tanh',
                        subsample_length=1))
model.add(MaxPooling1D(pool_length=pool_length))
model.add(LSTM(lstm_output_size))
model.add(Dense(1))
model.add(Activation('sigmoid'))

model.compile(loss='binary_crossentropy',
          optimizer='adam',
          metrics=['accuracy'])

model.fit(X_train, y_train, batch_size=batch_size, nb_epoch=20,
          validation_data=(X_test, y_test))