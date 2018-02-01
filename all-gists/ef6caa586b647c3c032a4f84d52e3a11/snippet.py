import numpy as np
import tensorflow as tf
from keras.callbacks import TensorBoard
from keras.layers import Input, Dense
from keras.models import Model


def write_log(callback, names, logs, batch_no):
    for name, value in zip(names, logs):
        summary = tf.Summary()
        summary_value = summary.value.add()
        summary_value.simple_value = value
        summary_value.tag = name
        callback.writer.add_summary(summary, batch_no)
        callback.writer.flush()
    
net_in = Input(shape=(3,))
net_out = Dense(1)(net_in)
model = Model(net_in, net_out)
model.compile(loss='mse', optimizer='sgd', metrics=['mae'])

log_path = './logs'
callback = TensorBoard(log_path)
callback.set_model(model)
train_names = ['train_loss', 'train_mae']
val_names = ['val_loss', 'val_mae']
for batch_no in range(100):
    X_train, Y_train = np.random.rand(32, 3), np.random.rand(32, 1)
    logs = model.train_on_batch(X_train, Y_train)
    write_log(callback, train_names, logs, batch_no)
    
    if batch_no % 10 == 0:
        X_val, Y_val = np.random.rand(32, 3), np.random.rand(32, 1)
        logs = model.train_on_batch(X_val, Y_val)
        write_log(callback, val_names, logs, batch_no//10)

