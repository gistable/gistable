# Time series forecasting based on multiple time series, including the original one
# This script is based on the following examples and discussions:
# https://gist.github.com/lukovkin/1aefa4509e066690b892
# https://groups.google.com/forum/#!topic/keras-users/9GsDwkSdqBg

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
import theano
from keras.models import Sequential  
from keras.layers.core import Dense, Activation, Dense, Dropout
from keras.layers.recurrent import LSTM, SimpleRNN, GRU

# Generate training data
#
# One time series is a COS function, influenced by a separate scale signal time series which is a set of multipliers (aka scales)
# for the COS function, that changes periodically. Furthermore, to validate that LSTM can spot changes that influence the
# time series ahead of time (i.e. changes acting as leading indicators), the COS time series is setup to adjusts its scale 
# with a 25 steps delay after the scale signal time series changes.

length = 3000 # Time series length
scales = [0.5, 1, 1.5] # By how much the COS function can be scaled
scale_step = 100 # How frequently to change scale factor
steps_ahead = 25 # How far ahead scale factor changes before the COS time series scale should change

df = pd.DataFrame(columns=['Series', 'Scale Signal'])

scale_signal = 1 #initial settings
scale = 1

for i in range(length):
    if (i + steps_ahead) % scale_step == 0:
        scale_signal = scales[random.randint(0, 2)]
    
    if i % scale_step == 0:
        scale = scale_signal
    
    df.loc[i,'Series'] = np.cos(i/4.0) * scale
    df.loc[i,'Scale Signal'] = scale_signal

# Prepare and format data for training
data = df.values
examples = 200 # how far back to look
y_examples = 100 # how many steps forward to predict
nb_samples = len(data) - examples - y_examples

input_list = [np.expand_dims(np.atleast_2d(data[i:examples+i,:]), axis=0) for i in xrange(nb_samples)]
input_mat = np.concatenate(input_list, axis=0)

# use the tail of the series as the test data
df_test = pd.DataFrame(df[-examples:])

test_data = df_test.values
test_input_list = [np.expand_dims(np.atleast_2d(test_data[len(test_data)-examples:len(test_data),:]), axis=0) for i in xrange(1)]
test_input_mat = np.concatenate(test_input_list, axis=0)

# target - the first column in df dataframe
target_list = [np.atleast_2d(data[i+examples:examples+i+y_examples,0]) for i in xrange(nb_samples)]
target_mat = np.concatenate(target_list, axis=0)

# set up model
features = input_mat.shape[2]
hidden = 128

model = Sequential()
model.add(LSTM(hidden, input_shape=(examples, features)))
model.add(Dropout(.2))
model.add(Dense(y_examples))
model.add(Activation('linear'))
model.compile(loss='mse', optimizer='rmsprop')

# Train
hist = model.fit(input_mat, target_mat, nb_epoch=100, batch_size=100, validation_split=0.05, show_accuracy=False)

# Get and plot predicted data and the validation loss
predicted = model.predict(test_input_mat)  

df_val_loss = pd.DataFrame(hist.history['val_loss'])
df_val_loss.plot()

df_predicted = pd.DataFrame(predicted).T
df_predicted.columns = ['Predicted']

df_result = pd.concat([df, df_predicted], ignore_index=True)
df_result.plot()

plt.show()
