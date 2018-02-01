# -*- coding: utf-8 -*-

# Copyright (C) 2017 by Akira TAMAMORI

# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

import tensorflow as tf
from tensorflow.python.ops.rnn_cell import RNNCell


class SRUCell(RNNCell):
    """Simple Recurrent Unit (SRU).

       This implementation is based on:

       Tao Lei and Yu Zhang,
       "Training RNNs as Fast as CNNs,"
       https://arxiv.org/abs/1709.02755
    """

    def __init__(self, num_units, activation=None, reuse=None):
        self._num_units = num_units
        self._activation = activation or tf.tanh

    @property
    def output_size(self):
        return self._num_units

    @property
    def state_size(self):
        return self._num_units

    def __call__(self, inputs, state, scope=None):
        """Run one step of SRU."""

        with tf.variable_scope(scope or type(self).__name__):  # "SRUCell"
            with tf.variable_scope("Inputs"):
                x = linear([inputs], self._num_units, False)
            with tf.variable_scope("Gate"):
                concat = tf.sigmoid(
                    linear([inputs], 2 * self._num_units, True))
                if tf.__version__ == "0.12.1":
                    f, r = tf.split(1, 2, concat)
                else:
                    f, r = tf.split(axis=1, num_or_size_splits=2, value=concat)

            c = f * state + (1 - f) * x

            # highway connection
            h = r * self._activation(c) + (1 - r) * inputs

        return h, c


def linear(args, output_size, bias, bias_start=0.0, scope=None):
    """Linear map: sum_i(args[i] * W[i]), where W[i] is a variable.
    Args:
      args: a 2D Tensor or a list of 2D, batch x n, Tensors.
      output_size: int, second dimension of W[i].
      bias: boolean, whether to add a bias term or not.
      bias_start: starting value to initialize the bias; 0 by default.
      scope: VariableScope for the created subgraph; defaults to "Linear".

    Returns:
      A 2D Tensor with shape [batch x output_size] equal to
      sum_i(args[i] * W[i]), where W[i]s are newly created matrices.

    Raises:
      ValueError: if some of the arguments has unspecified or wrong shape.
    """
    if args is None or (isinstance(args, (list, tuple)) and not args):
        raise ValueError("`args` must be specified")
    if not isinstance(args, (list, tuple)):
        args = [args]

    # Calculate the total size of arguments on dimension 1.
    total_arg_size = 0
    shapes = [a.get_shape().as_list() for a in args]
    for shape in shapes:
        if len(shape) != 2:
            raise ValueError(
                "Linear is expecting 2D arguments: %s" % str(shapes))
        if not shape[1]:
            raise ValueError(
                "Linear expects shape[1] of arguments: %s" % str(shapes))
        else:
            total_arg_size += shape[1]

    # Now the computation.
    with tf.variable_scope(scope or "Linear"):
        matrix = tf.get_variable("Matrix", [total_arg_size, output_size])
        if len(args) == 1:
            res = tf.matmul(args[0], matrix)
        else:
            res = tf.matmul(tf.concat(1, args), matrix)
        if not bias:
            return res
        bias_term = tf.get_variable(
            "Bias", [output_size],
            initializer=tf.constant_initializer(bias_start))
    return res + bias_term
