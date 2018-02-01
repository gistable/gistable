import theano
from keras.models import Sequential
from keras.layers.core import Dense, Activation

X_train, y_train = ... # load some training data
X_batch = ... # a batch of test data

# this is your initial model
model = Sequential()
model.add(Dense(20, 64))
model.add(Activation('tanh'))
model.add(Dense(64, 1))

# we train it
model.compile(loss='mse', optimizer='sgd')
model.fit(X_train, y_train, nb_epoch=20, batch_size=16)

# we define a function that returns the activation of layer 1 (after the tanh)
get_layer_1 = theano.function([model.layers[0].input], model.layers[1].output(train=False), allow_input_downcast=True)
transformed_data = get_layer_1(X_batch) # activation of layer 1