# Time Series Testing 
import keras.callbacks
from keras.models import Sequential  
from keras.layers.core import Dense, Activation, Dense, Dropout
from keras.layers.recurrent import LSTM

# Call back to capture losses 
class LossHistory(keras.callbacks.Callback):
    def on_train_begin(self, logs={}):
        self.losses = []

    def on_batch_end(self, batch, logs={}):
        self.losses.append(logs.get('loss'))
        
# You should get data frames with prices somewhere, e.g. on Quandl - implementation is up to you
# merge data frames
merged = df1.merge(df2, left_index=True, right_index=True, how='inner').dropna()

# data prep
# use 100 days of historical data to predict 10 days in the future
data = merged.values
examples = 100
y_examples = 10
nb_samples = len(data) - examples - y_examples

# input - 2 features
input_list = [np.expand_dims(np.atleast_2d(data[i:examples+i,:]), axis=0) for i in xrange(nb_samples)]
input_mat = np.concatenate(input_list, axis=0)

# target - the first column in merged dataframe
target_list = [np.atleast_2d(data[i+examples:examples+i+y_examples,0]) for i in xrange(nb_samples)]
target_mat = np.concatenate(target_list, axis=0)

# set up model
trials = input_mat.shape[0]
features = input_mat.shape[2]
hidden = 64
model = Sequential()
model.add(LSTM(hidden, input_shape=(examples, features)))
model.add(Dropout(.2))
model.add(Dense(y_examples))
model.add(Activation('linear'))
model.compile(loss='mse', optimizer='rmsprop')

# Train
history = LossHistory()
model.fit(input_mat, target_mat, nb_epoch=100, batch_size=400, callbacks=[history])
