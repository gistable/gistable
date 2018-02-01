import numpy as np
import tensorflow as tf

# N, size of matrix. R, rank of data
N = 100
R = 5

# generate data
W_true = np.random.randn(N,R)
C_true = np.random.randn(R,N)
Y_true = np.dot(W_true, C_true)
Y_tf = tf.constant(Y_true.astype(np.float32))

W = tf.Variable(np.random.randn(N,R).astype(np.float32))
C = tf.Variable(np.random.randn(R,N).astype(np.float32))
Y_est = tf.matmul(W,C)
loss = tf.reduce_sum((Y_tf-Y_est)**2)

# regularization 
alpha = tf.constant(1e-4)
regW = alpha*tf.reduce_sum(W**2)
regC = alpha*tf.reduce_sum(C**2)

# full objective
objective = loss + regW + regC

# optimization setup
train_step = tf.train.AdamOptimizer(0.001).minimize(objective)

# fit the model
init_op = tf.initialize_all_variables()
with tf.Session() as sess:
    sess.run(init_op)
    for n in range(10000):
        sess.run(train_step)
        if (n+1) % 1000 == 0:
            print('iter %i, %f' % (n+1, sess.run(objective)))
