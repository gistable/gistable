import tensorflow as tf
tf.reset_default_graph()

from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)

### model ###

# input
with tf.name_scope('input') as scope:
    x = tf.placeholder(tf.float32, [None, 28*28], name="input")
    # a placeholder to hold the correct answer during training
    labels = tf.placeholder(tf.float32, [None, 10], name="label")
    # the probability of a neuron being kept during dropout
    keep_prob = tf.placeholder(tf.float32, name="keep_prob")

with tf.name_scope('model') as scope:
    with tf.name_scope('fc1') as scope: # fc1 stands for 1st fully connected layer
        # 1st layer goes from 784 neurons (input) to 500 in the first hidden layer
        w1 = tf.Variable(tf.truncated_normal([28*28, 500], stddev=0.1), name="weights")
        b1 = tf.Variable(tf.constant(0.1, shape=[500]), name="biases")

        with tf.name_scope('softmax_activation') as scope:
            # softmax activation
            a1 = tf.nn.softmax(tf.matmul(x, w1) + b1)

        with tf.name_scope('dropout') as scope:
            # dropout
            drop1 = tf.nn.dropout(a1, keep_prob)

    with tf.name_scope('fc2') as scope:
        # takes the first hidden layer of 500 neurons to 100 (second hidden layer)
        w2 = tf.Variable(tf.truncated_normal([500, 100], stddev=0.1), name="weights")
        b2 = tf.Variable(tf.constant(0.1, shape=[100]), name="biases")

        with tf.name_scope('relu_activation') as scope:
            # relu activation, and dropout for second hidden layer
            a2 = tf.nn.relu(tf.matmul(drop1, w2) + b2)

        with tf.name_scope('dropout') as scope:
            drop2 = tf.nn.dropout(a2, keep_prob)

    with tf.name_scope('fc3') as scope:
        # takes the second hidden layer of 100 neurons to 10 (which is the output)
        w3 = tf.Variable(tf.truncated_normal([100, 10], stddev=0.1), name="weights")
        b3 = tf.Variable(tf.constant(0.1, shape=[10]), name="biases")

        with tf.name_scope('logits') as scope:
            # final layer doesn't have dropout
            logits = tf.matmul(drop2, w3) + b3

with tf.name_scope('train') as scope:
    with tf.name_scope('loss') as scope:
        # loss function
        cross_entropy = tf.nn.softmax_cross_entropy_with_logits(labels=labels, logits=logits)
    # use adam optimizer for training with a learning rate of 0.001
    train_step = tf.train.AdamOptimizer(0.001).minimize(cross_entropy)

with tf.name_scope('evaluation') as scope:
    # evaluation
    correct_prediction = tf.equal(tf.argmax(logits,1), tf.argmax(labels,1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

# create a summarizer that summarizes loss and accuracy
tf.summary.scalar("Accuracy", accuracy)

# add average loss summary over entire batch
tf.summary.scalar("Loss", tf.reduce_mean(cross_entropy)) 

# merge summaries
summary_op = tf.summary.merge_all()

# create saver object
saver = tf.train.Saver()

### training ###

with tf.Session() as sess:
    # initialize variables
    tf.global_variables_initializer().run()
    
    # initialize summarizer filewriter
    fw = tf.summary.FileWriter("/tmp/nn/summary", sess.graph)

    # train the network
    for step in range(20000):
        batch_xs, batch_ys = mnist.train.next_batch(100)
        sess.run(train_step, feed_dict={x: batch_xs, labels: batch_ys, keep_prob:0.2})

        if step%1000 == 0:
            acc = sess.run(accuracy, feed_dict={
                x: batch_xs, labels: batch_ys, keep_prob:1})
            print("mid train accuracy:", acc, "at step:", step)
        
        if step%100 == 0:
            # compute summary using test data every 100 steps
            summary = sess.run(summary_op, feed_dict={
                x: mnist.test.images, labels: mnist.test.labels, keep_prob:1})

        # add merged summaries to filewriter,
        # so they are saved to disk
        fw.add_summary(summary, step)
    
    # save trained model
    saver.save(sess, "/tmp/nn/my_nn.ckpt")