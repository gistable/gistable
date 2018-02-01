import numpy as np
import tensorflow as tf

# Newton's optimization method for multivariate function in tensorflow

def cons(x):
    return tf.constant(x, dtype=tf.float32)

def compute_hessian(fn, vars):
    mat = []
    for v1 in vars:
        temp = []
        for v2 in vars:
            temp.append(tf.gradients(tf.gradients(fn, v2)[0], v1)[0])
        temp = [cons(0) if t == None else t for t in temp]
        temp = tf.pack(temp)
        mat.append(temp)
    mat = tf.pack(mat)
    return mat

def compute_grads(fn, vars):
    grads = []
    for v in vars:
        grads.append(tf.gradients(fn, v)[0])
    return tf.reshape(tf.pack(grads), shape=[2, -1])

def optimize(all_variables, update):
    optmize_variables = []
    for i in range(len(all_variables)):
        optmize_variables.append(all_variables[i].assign(all_variables[i] - alpha * tf.squeeze(update[i])))
    return tf.pack(optmize_variables)

x = tf.Variable(np.random.random_sample(), dtype=tf.float32)
y = tf.Variable(np.random.random_sample(), dtype=tf.float32)

alpha = cons(0.1)

# f = tf.pow(x, cons(2)) + cons(2) * x * y + cons(3) * tf.pow(y, cons(2)) + cons(4) * x + cons(5) * y + cons(6)
f = cons(0.5) * tf.pow(x, 2) + cons(2.5) * tf.pow(y, 2)
all_variables = [x, y]

hessian = compute_hessian(f, all_variables)
hessian_inv = tf.matrix_inverse(hessian)
g = compute_grads(f, all_variables)
update = tf.unpack(tf.matmul(hessian_inv, g))

optimize_op = optimize(all_variables, update)

sess = tf.Session()
sess.run(tf.initialize_all_variables())

func = np.inf
for i in range(10):
    prev = func
    v1, v2, func = sess.run([x, y, f])
    print v1, v2, func
    sess.run(optimize_op)
