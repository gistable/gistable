'''
A logistic regression example using the meta-graph checkpointing
features of Tensorflow.

Author: João Felipe Santos, based on code by Aymeric Damien
(https://github.com/aymericdamien/TensorFlow-Examples/)
'''

from __future__ import print_function

import tensorflow as tf
import numpy as np
import argparse

# Import MNIST data
from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("/tmp/data/", one_hot=True)

# Parameters
learning_rate = 0.01
batch_size = 100
display_step = 1

parser = argparse.ArgumentParser()
parser.add_argument('--load', default=False)
parser.add_argument('--max_epochs', type=int, default=5)
args = parser.parse_args()
load = args.load
training_epochs = args.max_epochs

# Instantiate saver
if not load:
    # tf Graph Input
    x = tf.placeholder(tf.float32, [None, 784], name='x') # mnist data image of shape 28*28=784
    y = tf.placeholder(tf.float32, [None, 10], name='y') # 0-9 digits recognition => 10 classes

    # Set model weights
    W = tf.Variable(tf.zeros([784, 10]), name='W')
    b = tf.Variable(tf.zeros([10]), name='b')

    # Construct model
    pred = tf.nn.softmax(tf.matmul(x, W) + b) # Softmax

    # Minimize error using cross entropy
    cost = tf.reduce_mean(-tf.reduce_sum(y*tf.log(pred), reduction_indices=1))
    # Gradient Descent
    optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(cost)

    init = tf.initialize_all_variables()

    saver = tf.train.Saver()
    # In order to be able to easily retrieve variables and ops later,
    # we add them to collections
    tf.add_to_collection('train_op', optimizer)
    tf.add_to_collection('cost_op', cost)
    tf.add_to_collection('input', x)
    tf.add_to_collection('target', y)
    tf.add_to_collection('pred', pred)

    initial_epoch = 0
else:
    # Find last executed epoch
    from glob import glob
    history = list(map(lambda x: int(x.split('-')[1][:-5]), glob('model.ckpt-*.meta')))
    last_epoch = np.max(history)
    # Instantiate saver object using previously saved meta-graph
    saver = tf.train.import_meta_graph('model.ckpt-{}.meta'.format(last_epoch))
    initial_epoch = last_epoch + 1

# Launch the graph
with tf.Session() as sess:
    if not load:
        sess.run(init)
    else:
        saver.restore(sess, 'model.ckpt')
        optimizer = tf.get_collection('train_op')[0]
        cost = tf.get_collection('cost_op')[0]
        x = tf.get_collection('input')[0]
        y = tf.get_collection('target')[0]
        pred = tf.get_collection('pred')[0]

    # Training cycle
    for epoch in range(initial_epoch, training_epochs):
        avg_cost = 0.
        total_batch = int(mnist.train.num_examples/batch_size)
        # Loop over all batches
        for i in range(total_batch):
            batch_xs, batch_ys = mnist.train.next_batch(batch_size)
            # Run optimization op (backprop) and cost op (to get loss value)
            _, c = sess.run([optimizer, cost], feed_dict={x: batch_xs,
                                                          y: batch_ys})
            # Compute average loss
            avg_cost += c / total_batch
        # Display logs per epoch step
        if (epoch+1) % display_step == 0:
            print("Epoch:", '%04d' % (epoch+1), "cost=", "{:.9f}".format(avg_cost))
        saver.save(sess, 'model.ckpt', global_step=epoch)

    print("Optimization Finished!")

    # Test model
    correct_prediction = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
    # Calculate accuracy
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
    print("Accuracy:", accuracy.eval({x: mnist.test.images, y: mnist.test.labels}))
