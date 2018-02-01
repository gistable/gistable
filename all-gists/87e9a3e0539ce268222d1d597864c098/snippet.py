import keras
import numpy as np

timesteps = 60
input_dim = 64
samples = 10000
batch_size = 128
output_dim = 64

# Test data.
x_np = np.random.random((samples, timesteps, input_dim))
y_np = np.random.random((samples, output_dim))

print('Classic stacked LSTM: 35s/epoch on CPU')
inputs = keras.Input((timesteps, input_dim))
x = keras.layers.LSTM(output_dim, return_sequences=True)(inputs)
x = keras.layers.LSTM(output_dim, return_sequences=True)(x)
x = keras.layers.LSTM(output_dim)(x)

classic_model = keras.models.Model(inputs, x)
classic_model.compile(optimizer='rmsprop', loss='mse')
classic_model.fit(x_np, y_np, batch_size=batch_size, epochs=4)

print('New stacked LSTM: 30s/epoch on CPU (15pct faster)')
cells = [
    keras.layers.LSTMCell(output_dim),
    keras.layers.LSTMCell(output_dim),
    keras.layers.LSTMCell(output_dim),
]

inputs = keras.Input((timesteps, input_dim))
x = keras.layers.RNN(cells)(inputs)

new_model = keras.models.Model(inputs, x)
new_model.compile(optimizer='rmsprop', loss='mse')
new_model.fit(x_np, y_np, batch_size=batch_size, epochs=4)
