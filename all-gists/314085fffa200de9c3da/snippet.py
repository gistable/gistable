'''Functional Keras is a more functional replacement for the Graph API.
'''

###################
# 2 LSTM branches #
###################
a = Input(input_shape=(10, 32))  # output is a TF/TH placeholder, augmented with Keras attributes
b = Input(input_shape=(10, 32))
encoded_a = LSTM(32)(a)  # output is a TF/TH tensor
encoded_b = LSTM(32)(b)
merged = merge([encoded_a, encoded_b], mode='concat')
decoded = RepeatVector(10)(merged)
decoded = LSTM(32, return_sequences=True)(decoded)

# this is a fully-featured Keras model, will all the goodies that come with those.
# this is made possible by Keras topology information stored in the tensors.
model = Model(input=[a, b], output=[decoded])
model.compile(optimizer=Adam(), loss='mse')
model.fit([x1, x2], y)

################
# Shared layer #
################
shared_lstm = LSTM(32)
a = Input(input_shape=(10, 32))
b = Input(input_shape=(10, 32))
encoded_a = shared_lstm(a)
encoded_b = shared_lstm(b)
merged = merge([encoded_a, encoded_b], mode='concat')
decoded = RepeatVector(10)(merged)
decoded = LSTM(32, return_sequences=True)(decoded)

##############################
# Insertion of arbitrary ops #
##############################
# NOTE: cannot do a = tf.sigmoid(a), because although 'a' is a valid tf tensor,
# it is 'augmented' with data that allows Keras to keep track of previous operations
# (thus making it possible to train a model)...
a = Input(input_shape=(10, 32))
a = Lambda(tf.sigmoid)(a)

model = Model(input=[a, b], output=[decoder])
model.compile(optimizer=Adam(), loss='mse')
model.fit([x1, x2], y)