import numpy as np
import tensorflow as tf
import scipy
from tensorflow.contrib.eager.python import tfe
tfe.enable_eager_execution()

# manual numpy example
# X = np.array(([[0., 1], [2, 3]]))
# W0 = X
# W1 = np.array(([[0., 1], [2, 3]]))/10
# W2 = np.array(([[4., 5], [6, 7]]))/10
# A1 = W0
# A2 = W1 @ A1
# A3 = W2 @ A2
# err = A3 - A1
# n = 2
# dsize = 2
# loss = np.sum(err*err)/dsize/2

# B2 = err
# B1 = W2.T @ B2
# B0 = W1.T @ B1
# dW1 = B1 @ A1.T/dsize
# dW2 = B2 @ A2.T/dsize


def main():
  np.random.seed(1)
  tf.set_random_seed(1)
  
  dtype = np.float32
  lambda_=3e-3
  lr = 0.2
  dsize = 2
  fs = [dsize, 2, 2, 2]  # layer sizes
  n = len(fs) - 2

  def t(mat): return tf.transpose(mat)

  def regularized_inverse(mat):
    n = int(mat.shape[0])
    return tf.linalg.inv(mat + lambda_*tf.eye(n, dtype=dtype))

  train_images = np.asarray([[0, 1], [2, 3]])
  X = tf.constant(train_images[:,:dsize].astype(dtype))

  W1_0 = np.asarray([[0., 1], [2, 3]]).astype(dtype)/10
  W2_0 = np.asarray([[4., 5], [6, 7]]).astype(dtype)/10
  W1 = tfe.Variable(W1_0, name='W1')
  W2 = tfe.Variable(W2_0, name='W2')

  forward = []
  backward = []
  forward_inv = []
  backward_inv = []
  @tfe.custom_gradient
  def capturing_matmul(W, A):
    forward.append(A)
    def grad(B):
      backward.append(B)
      return [B @ tf.transpose(A), tf.transpose(W) @ B]
    return W @ A, grad


  @tfe.custom_gradient
  def kfac_matmul(W, A):
    def grad(B):
      m1 = tf.transpose(backward_inv.pop())
      m2 = forward_inv.pop()
      true_grad1 = B @ tf.transpose(A)
      true_grad2 = tf.transpose(W) @ B
      return [m1 @ true_grad1 @ m2, true_grad2]
    return W @ A, grad


  matmul = tf.matmul
  nonlin = tf.nn.sigmoid
  def loss_fn(synthetic=False):
    x = nonlin(matmul(W1, X))
    x = nonlin(matmul(W2, x))
    if synthetic:
      val = np.random.randn(*X.shape).astype(dtype)
      target = tf.constant((x + tf.constant(val)).numpy())
    else:
      target = X
    err = target-x
    loss = tf.reduce_sum(err*err)/2/dsize
    return loss
  
  loss_and_grads = tfe.implicit_value_and_gradients(loss_fn)
  optimizer = tf.train.GradientDescentOptimizer(learning_rate=lr)
  for step in range(10):
    del backward[:]
    del forward[:]
    del forward_inv[:]
    del backward_inv[:]

    matmul = capturing_matmul
    loss, grads_and_vars = loss_and_grads(True)
    backward.reverse()

    for i in range(len(backward)):
      backward[i] = backward[i]*dsize
      
    def cov(X): return X @ t(X)/dsize
    def invcov(X): return regularized_inverse(cov(X))
      
    for i in range(n):
      forward_inv.append(invcov(forward[i]))
      backward_inv.append(invcov(backward[i]))

    matmul = kfac_matmul
    loss, grads_and_vars = loss_and_grads()
    print("Step %3d loss %10.9f"%(step, loss.numpy()))
    optimizer.apply_gradients(grads_and_vars)

  target = 3.851136208  # linear activation
  target = 1.256854534  # with broken random sampling
  target = 1.251557469  # with proper random sampling

  assert abs(loss.numpy()-target)<1e-9, abs(loss.numpy()-target)

if __name__=='__main__':
  main()
