import tensorflow as tf

"""
Multi dimensional softmax,
refer to https://github.com/tensorflow/tensorflow/issues/210

compute softmax along the dimension of target
the native softmax only supports batch_size x dimension
"""
def softmax(target, axis, name=None):
  with tf.name_scope(name, 'softmax', values=[target]):
    max_axis = tf.reduce_max(target, axis, keep_dims=True)
    target_exp = tf.exp(target-max_axis)
    normalize = tf.reduce_sum(target_exp, axis, keep_dims=True)
    softmax = target_exp / normalize
    return softmax