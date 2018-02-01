# Stacked LSTMs
# Author: Kyle Kastner
# Based on script from /u/siblbombs
# License: BSD 3-Clause
import tensorflow as tf
from tensorflow.models.rnn import rnn
from tensorflow.models.rnn.rnn_cell import LSTMCell
import numpy as np
import time

log_device_placement = True
np.random.seed(1)
batch_size = 100
n_steps = 250

input_dim = 50
hidden_dim = 70
output_dim = 20


#  Sequences we will provide at runtime
seq_input = tf.placeholder(tf.float32, [n_steps, batch_size, input_dim])

#  What timestep we want to stop at
early_stop = tf.placeholder(tf.int32)

initializer = tf.random_uniform_initializer(-1, 1)

#  Inputs for rnn needs to be a list, each item being a timestep.
#  we need to split our input into each timestep, and reshape it because
#  split keeps dims by default
inputs = [tf.reshape(i, (batch_size, input_dim))
          for i in tf.split(0, n_steps, seq_input)]


with tf.device("/cpu:0"):
    cell1 = LSTMCell(hidden_dim, input_dim, initializer=initializer)
    initial_state1 = cell1.zero_state(batch_size, tf.float32)
    outputs1, states1 = rnn.rnn(cell1, inputs, initial_state=initial_state1,
                                sequence_length=early_stop, scope="RNN1")

with tf.device("/cpu:0"):
    cell2 = LSTMCell(output_dim, hidden_dim, initializer=initializer)
    initial_state2 = cell2.zero_state(batch_size, tf.float32)
    outputs2, states2 = rnn.rnn(cell2, outputs1, initial_state=initial_state2,
                                sequence_length=early_stop, scope="RNN2")

# Create initialize op, this needs to be run by the session!
iop = tf.initialize_all_variables()

# Create session with device logging
session = tf.Session(
    config=tf.ConfigProto(log_device_placement=log_device_placement))

# Actually initialize, if you don't do this you get errors about uninitialized
session.run(iop)

# First call to session has overhead? lets get that cleared out
t1 = time.time()
feed = {early_stop: 2,
        seq_input: np.random.rand(
            n_steps, batch_size, input_dim).astype('float32')}
outs = session.run(outputs2, feed_dict=feed)
t2 = time.time()
print("Time for first call to session.run %f" % (t2 - t1))

for e_s in [10, 50, 100, 150, 200, 250]:
    feed = {early_stop: e_s,
            seq_input: np.random.rand(
                n_steps, batch_size, input_dim).astype('float32')}
    t1 = time.time()
    #  Early_stop can be varied, but seq_input needs to match the earlier shape
    outs = session.run(outputs2, feed_dict=feed)
    t2 = time.time()
    #  Output is a list, each item being a single timestep.
    #  Items at t>early_stop are all 0s
    print("Time for %i: %f" % (e_s, t2 - t1))