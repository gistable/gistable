import tensorflow as tf
from tensorflow.python.framework import ops
import numpy as np

# Define custom py_func which takes also a grad op as argument:
def py_func(func, inp, Tout, stateful=True, name=None, grad=None):
    
    # Need to generate a unique name to avoid duplicates:
    rnd_name = 'PyFuncGrad' + str(np.random.randint(0, 1E+8))
    
    tf.RegisterGradient(rnd_name)(grad)  # see _MySquareGrad for grad example
    g = tf.get_default_graph()
    with g.gradient_override_map({"PyFunc": rnd_name}):
        return tf.py_func(func, inp, Tout, stateful=stateful, name=name)

# Def custom square function using np.square instead of tf.square:
def mysquare(x, name=None):
    
    with ops.op_scope([x], name, "Mysquare") as name:
        sqr_x = py_func(np.square,
                        [x],
                        [tf.float32],
                        name=name,
                        grad=_MySquareGrad)  # <-- here's the call to the gradient
        return sqr_x[0]

# Actual gradient:
def _MySquareGrad(op, grad):
    x = op.inputs[0]
    return grad * 20 * x  # add a "small" error just to see the difference:

with tf.Session() as sess:
    x = tf.constant([1., 2.])
    y = mysquare(x)
    tf.initialize_all_variables().run()

    print(x.eval(), y.eval(), tf.gradients(y, x)[0].eval())