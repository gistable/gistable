
class multiAttentionRNN(Recurrent):
    '''
    Word by Word attention model 
    # Arguments
        output_dim: output_dimensions
        init: weight initialization function.
            Can be the name of an existing function (str),
            or a Theano function (see: [initializations](../initializations.md)).
        inner_init: initialization function of the inner cells.
        activation: activation function.
            Can be the name of an existing function (str),
            or a Theano function (see: [activations](../activations.md)).
    # Comments:
        Takes in as input a concatenation of the vectors YH, where Y is the vectors being attended on and
        H are the vectors on which attention is being applied
    # References
        - [REASONING ABOUT ENTAILMENT WITH NEURAL ATTENTION](http://arxiv.org/abs/1509.06664v2)
    '''

    def __init__(self, output_dim,
                 init='glorot_uniform', inner_init='orthogonal',
                 W_regularizer=None, U_regularizer=None,
                 dropout_W=0., dropout_U=0., **kwargs):
        self.output_dim = output_dim
        self.init = initializations.get(init)
        self.inner_init = initializations.get(inner_init)
        self.W_regularizer = regularizers.get(W_regularizer)
        self.U_regularizer = regularizers.get(U_regularizer)
        self.dropout_W, self.dropout_U = dropout_W, dropout_U

        if self.dropout_W or self.dropout_U:
            self.uses_learning_phase = True
        super(multiAttentionRNN, self).__init__(**kwargs)

    def build(self, input_shape):
        self.input_spec = [InputSpec(shape=input_shape)]
        input_dim = input_shape[2]
        self.input_dim = input_dim

        if self.stateful:
            self.reset_states()
        else:
            # initial states: all-zero tensor of shape (output_dim)
            self.states = [None]
        
        self.W_y = self.init((input_dim, self.output_dim),
                           name='{}_W_y'.format(self.name))

        self.W_h = self.init((input_dim, self.output_dim),
                           name='{}_W_h'.format(self.name))

        self.W = self.init((self.output_dim, 1),
                           name='{}_W'.format(self.name))

        self.U_r = self.inner_init((self.output_dim, self.output_dim),
                                 name='{}_U_r'.format(self.name))

        self.U_t = self.inner_init((self.output_dim, self.output_dim),
                                 name='{}_U_t'.format(self.name))

        self.regularizers = []
        if self.W_regularizer:
            self.W_regularizer.set_param(K.concatenate([self.W_y,
                                                        self.W_h,
                                                        self.W]))
            self.regularizers.append(self.W_regularizer)
        if self.U_regularizer:
            self.U_regularizer.set_param(K.concatenate([self.U_r,
                                                        self.U_t]))
            self.regularizers.append(self.U_regularizer)

        self.trainable_weights = [self.W_y, self.W_h, self.W,
                                  self.U_r, self.U_t]

        if self.initial_weights is not None:
            self.set_weights(self.initial_weights)
            del self.initial_weights

    def reset_states(self):
        assert self.stateful, 'Layer must be stateful.'
        input_shape = self.input_spec[0].shape
        if not input_shape[0]:
            raise Exception('If a RNN is stateful, a complete ' +
                            'input_shape must be provided (including batch size).')
        if hasattr(self, 'states'):
            K.set_value(self.states[0],
                        np.zeros((input_shape[0], self.output_dim)))
        else:
            self.states = [K.zeros((input_shape[0], self.output_dim))]

    def preprocess_input(self, x):
        # xmaxlen is just the size of Y matrix to separate YH into Y and H.
        self.Y = x[:,:K.params['xmaxlen'],:]
        x = x[:,K.params['xmaxlen']:,:]

        return x

    def step(self, x, states):
        r_tm1 = states[0]
        B_U = states[1]
        B_W = states[2]

        L = K.params['xmaxlen']

        M = K.tanh(K.dot(self.Y, self.W_y) + K.repeat_elements(K.dot(x, self.W_h).dimshuffle((0,'x',1)),L, axis=1) + K.repeat_elements(K.dot(r_tm1, self.U_r).dimshuffle((0,'x',1)),L, axis=1))        
        alpha = K.dot(M, self.W)
        alpha = K.softmax(alpha[:,:,0]) 
        alpha = alpha.dimshuffle((0,'x',1))
        
        output = T.batched_dot(alpha,self.Y) + K.tanh(K.dot(r_tm1.dimshuffle((0,'x',1)), self.U_t))
        output = output[:,0,:]
        return output, [output]

    def get_constants(self, x):
        constants = []
        if 0 < self.dropout_U < 1:
            ones = K.ones_like(K.reshape(x[:, 0, 0], (-1, 1)))
            ones = K.concatenate([ones] * self.output_dim, 1)
            B_U = [K.dropout(ones, self.dropout_U) for _ in range(2)]
            constants.append(B_U)
        else:
            constants.append([K.cast_to_floatx(1.) for _ in range(2)])

        if self.consume_less == 'cpu' and 0 < self.dropout_W < 1:
            input_shape = self.input_spec[0].shape
            input_dim = input_shape[-1]
            ones = K.ones_like(K.reshape(x[:, 0, 0], (-1, 1)))
            ones = K.concatenate([ones] * input_dim, 1)
            B_W = [K.dropout(ones, self.dropout_W) for _ in range(3)]
            constants.append(B_W)
        else:
            constants.append([K.cast_to_floatx(1.) for _ in range(3)])
        return constants

    def get_config(self):
        config = {"output_dim": self.output_dim,
                  "init": self.init.__name__,
                  "inner_init": self.inner_init.__name__,
                  "activation": self.activation.__name__,
                  "W_regularizer": self.W_regularizer.get_config() if self.W_regularizer else None,
                  "U_regularizer": self.U_regularizer.get_config() if self.U_regularizer else None,
                  "b_regularizer": self.b_regularizer.get_config() if self.b_regularizer else None,
                  "dropout_W": self.dropout_W,
                  "dropout_U": self.dropout_U}
        base_config = super(SimpleRNN, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))