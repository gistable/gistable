class MyLSTMCell(tf.nn.rnn_cell.RNNCell):
    """Simplified Version rnn_cell.BasicLSTMCell"""
    def __init__(self, num_units):
        super(MyLSTMCell, self).__init__()
        self._num_units = num_units

    def __call__(self, inputs, state, scope="LSTM"):
        with tf.variable_scope(scope):
            c, h = state

            gates  = layers.fully_connected(tf.concat(1, [inputs, h]),
                                            num_outputs=4 * self._num_units,
                                            activation_fn=None)
            # i = input_gate, j = new_input, f = forget_gate, o = output_gate
            i, j, f, o = tf.split(1, 4, gates)

            forget_bias = 1.0
            new_c = (c * tf.nn.sigmoid(f + forget_bias)
                     + tf.nn.sigmoid(i) * tf.nn.tanh(j))
            new_h =  tf.nn.tanh(new_c) * tf.nn.sigmoid(o)

            return new_h, (new_c, new_h)

    def zero_state(self, batch_size, dtype=tf.float32, learnable=False, scope="LSTM"):
        if learnable:
            c = tf.get_variable("c_init", (1, self._num_units),
                    initializer=tf.random_normal_initializer(dtype=dtype))
            h = tf.get_variable("h_init", (1, self._num_units),
                    initializer=tf.random_normal_initializer(dtype=dtype))
        else:
            c = tf.zeros((1, self._num_units), dtype=dtype)
            h = tf.zeros((1, self._num_units), dtype=dtype)
        c = tf.tile(c, [batch_size, 1])
        h = tf.tile(h, [batch_size, 1])
        c.set_shape([None, self._num_units])
        h.set_shape([None, self._num_units])
        return (c, h)

    @property
    def state_size(self):
        return (self._num_units, self._num_units)

    @property
    def output_size(self):
        return self._num_units