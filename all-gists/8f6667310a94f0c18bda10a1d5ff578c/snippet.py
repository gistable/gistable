import tensorflow as tf

from tensorflow.python.ops import init_ops
from tensorflow.python.ops import array_ops
from tensorflow.python.ops import math_ops
from tensorflow.python.ops.rnn_cell_impl import RNNCell, _linear

class LRUCell(RNNCell): 
    """Lattice Recurrent Unit (LRU).
       This implementation is based on:
       C. Ahuja and L.-P. Morency (2017)
       "Lattice Recurrent Unit: Improving Convergence and Statistical Efficiency for Sequence Modeling"
       https://arxiv.org/abs/1710.02254
       Note that this is the implementation of the (Update-Gate) LRU cell (best performing and last cell architecture)
    """

    def __init__(self, 
                 num_units,
                 kernel_initializer=None, 
                 bias_initializer=None):
      """Initialize the parameters for an LRU cell.
        Args:
          num_units: int, number of units in the LRU cell
          kernel_initializer: (optional) The initializer to use for the weight and
            projection matrices.
          bias_initializer: (optional) The initializer to use for the bias matrices. 
            Default: vectors of ones.
      """
      super(LRUCell, self).__init__(_reuse=True)

      self._num_units = num_units
      self._kernel_initializer = kernel_initializer
      self._bias_initializer = bias_initializer

    @property
    def state_size(self):
      return self._num_units

    @property
    def output_size(self):
      return self._num_units

    def __call__(self, inputs, state, scope=None):
        """Run one step of LRU.
          Args:
            inputs: input Tensor, 2D, batch x num_units.
            state: a state Tensor, `2-D, batch x state_size`. 
          Returns:
            A tuple containing:
            - A `2-D, [batch x num_units]`, Tensor representing the output of the
              LRU after reading `inputs` when previous state was `state`.
            - A `2-D, [batch x num_units]`, Tensor representing the new state of LRU after reading `inputs` when
              the previous state was `state`.  Same type and shape(s) as `state`.
          Raises:
            ValueError: 
            - If input size cannot be inferred from inputs via
              static shape inference.
            - If state is not `2D`.
        """
        if inputs.get_shape()[1] != self._num_units:
            with tf.variable_scope("input_transformation"):  
                W = tf.get_variable("kernel", [inputs.get_shape()[1], self._num_units], initializer = self._kernel_initializer)
                inputs = tf.matmul(inputs, W)

        ## r_1, r_2, z_1 and z_2  update & reset gates (resp. eq. 11, 12, 15 & 16)
        with tf.variable_scope("gates"):  
            # We start with bias of 1.0 to not reset and not update.
            bias_ones = self._bias_initializer
            if self._bias_initializer is None:
              dtype = [a.dtype for a in [inputs, state]][0]
              bias_ones = init_ops.constant_initializer(1.0, dtype=dtype)
            value = math_ops.sigmoid(
                _linear([inputs, state], 4 * self._num_units, True, bias_ones,
                        self._kernel_initializer))
            r1, r2, z1, z2 = array_ops.split(value=value, num_or_size_splits=4, axis=1)

        ## h1_hat
        with tf.variable_scope("projected_state1"):
            bias_ones = self._bias_initializer
            if self._bias_initializer is None:
              dtype = [a.dtype for a in [inputs, state]][0]
              bias_ones = init_ops.constant_initializer(1.0, dtype=dtype)
            h1_hat = tf.tanh(
                _linear([inputs, r2 * state], self._num_units, True, bias_ones,
                        self._kernel_initializer))
        ## h2_hat
        with tf.variable_scope("projected_state2"):
            bias_ones = self._bias_initializer
            if self._bias_initializer is None:
              dtype = [a.dtype for a in [inputs, state]][0]
              bias_ones = init_ops.constant_initializer(1.0, dtype=dtype)
            h2_hat = tf.tanh(
                _linear([r1 * inputs, state], self._num_units, True, bias_ones,
                        self._kernel_initializer))

        h1_prime = z1 * h2_hat + (1 - z1) * inputs
        h2_prime = z2 * h1_hat + (1 - z2) * state

        return h1_prime, h2_prime

