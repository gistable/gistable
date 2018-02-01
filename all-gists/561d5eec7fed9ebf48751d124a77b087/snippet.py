import tensorflow as tf
from tensorflow.python.framework import ops
from tensorflow.python.ops import gen_nn_ops

@ops.RegisterGradient("GuidedRelu")
def _GuidedReluGrad(op, grad):
    return tf.select(0. < grad, gen_nn_ops._relu_grad(grad, op.outputs[0]), tf.zeros(grad.get_shape()))

if __name__ == '__main__':
    with tf.Session() as sess:
        g = tf.get_default_graph()
        x = tf.constant([10., 2.])
        with g.gradient_override_map({'Relu': 'GuidedRelu'}):
            y = tf.nn.relu(x)
            z = tf.reduce_sum(-y ** 2)
        tf.initialize_all_variables().run()

        print x.eval(), y.eval(), z.eval(), tf.gradients(z, x)[0].eval()
        # > [ 10.   2.] [ 10.   2.] -104.0 [ 0.  0.]
