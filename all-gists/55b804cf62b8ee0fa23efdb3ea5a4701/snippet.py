from keras.layers import Recurrent
import keras.backend as K
from keras import activations
from keras import initializers
from keras import regularizers
from keras import constraints
from keras.engine import Layer
from keras.engine import InputSpec


class RWA(Recurrent):
    """
    # References 
     - [Machine Learning on Sequential Data Using a Recurrent Weighted Average](https://arxiv.org/abs/1703.01253)
    """
    @interfaces.legacy_recurrent_support
    def __init__(self, units,
                 activation='tanh',
                 recurrent_activation='tanh',
                 features_initializer='glorot_uniform',
                 recurrent_initializer='glorot_uniform',
                 average_initializer = 'glorot_uniform',
                 initial_attention_initializer = 'zeros',
                 bias_initializer='zeros',
                 features_regularizer=None,
                 recurrent_regularizer=None,
                 average_regularizer=None,
                 initial_attention_regularizer = None,
                 bias_regularizer=None,
                 features_constraint=None,
                 recurrent_constraint=None,
                 average_constraint=None,
                 initial_attention_constraint = None,
                 bias_constraint=None,
#                  dropout=0.,
#                  recurrent_dropout=0.,
                 **kwargs):
        super(RWA, self).__init__(**kwargs)
        self.units = units
        self.activation = activations.get(activation)
        self.recurrent_activation = activations.get(recurrent_activation)
        self.supports_masking = False
        self.unroll = False
        self.return_sequences = False
        self.go_backwards = False
        self.features_initializer = initializers.get(features_initializer)
        self.recurrent_initializer = initializers.get(recurrent_initializer)
        self.average_initializer = initializers.get(average_initializer)
        self.initial_attention_initializer = initializers.get(initial_attention_initializer)
        self.bias_initializer = initializers.get(bias_initializer)

        self.features_regularizer = regularizers.get(features_regularizer)
        self.recurrent_regularizer = regularizers.get(recurrent_regularizer)
        self.average_regularizer = regularizers.get(average_regularizer)
        self.initial_attention_regularizer = regularizers.get(initial_attention_regularizer)
        self.bias_regularizer = regularizers.get(bias_regularizer)


        self.features_constraint = constraints.get(features_constraint)
        self.recurrent_constraint = constraints.get(recurrent_constraint)
        self.average_constraint = constraints.get(average_constraint)
        self.initial_attention_constraint = constraints.get(initial_attention_constraint)
        self.bias_constraint = constraints.get(bias_constraint)

#         self.dropout = min(1., max(0., dropout))
#         self.recurrent_dropout = min(1., max(0., recurrent_dropout))

        
        
    def call(self, inputs, mask=None, initial_state=None, training=None):
        # input shape: `(samples, time (padded with zeros), input_dim)`
        # note that the .build() method of subclasses MUST define
        # self.input_spec and self.state_spec with complete input shapes.
        if initial_state is not None:
            if not isinstance(initial_state, (list, tuple)):
                initial_states = [initial_state]
            else:
                initial_states = list(initial_state)
        if isinstance(inputs, list):
            initial_states = inputs[1:]
            inputs = inputs[0]
        else:
            initial_states = self.get_initial_states(inputs)

        if len(initial_states) != len(self.states):
            raise ValueError('Layer has ' + str(len(self.states)) +
                             ' states but was passed ' +
                             str(len(initial_states)) +
                             ' initial states.')
        input_shape = K.int_shape(inputs)
        constants = self.get_constants(inputs, training=None)
        preprocessed_input = self.preprocess_input(inputs, training=None)
        h = initial_states[0]
        h+= self.recurrent_activation(self.initial_attention)
        initial_states[0]=h
        last_output, outputs, states = K.rnn(self.step,
                                             preprocessed_input,
                                             initial_states,
                                             go_backwards=self.go_backwards,
                                             mask=mask,
                                             constants=constants,
                                             unroll=self.unroll,
                                             input_length=input_shape[1])
        return last_output
#         if self.stateful:
#             updates = []
#             for i in range(len(states)):
#                 updates.append((self.states[i], states[i]))
#             self.add_update(updates, inputs)

        # Properly set learning phase
#         if 0 < self.dropout + self.recurrent_dropout:
#             last_output._uses_learning_phase = True
#             outputs._uses_learning_phase = True

#         if self.return_sequences:
#             return outputs
#         else:
#             return last_output
        
    def compute_output_shape(self, input_shape):
        if isinstance(input_shape, list):
            input_shape = input_shape[0]
        return (input_shape[0], self.units)
    
    def build(self, input_shape):
        if isinstance(input_shape, list):
            input_shape = input_shape[0]

        batch_size = None
        self.input_dim = input_shape[2]
        self.input_spec = InputSpec(shape=(batch_size, None, self.input_dim))
        #states: h, d, n, a_max
        self.state_spec = [InputSpec(shape=(batch_size, self.units)),
                           InputSpec(shape=(batch_size, self.units)),
                          InputSpec(shape=(batch_size, self.units)),
                          InputSpec(shape=(batch_size, self.units))]

        self.states = [None, None, None, None]
        #W_u and b_u
        self.features_kernel = self.add_weight((self.input_dim, self.units),
                                      name='features_kernel',
                                      initializer=self.features_initializer,
                                      regularizer=self.features_regularizer,
                                      constraint=self.features_constraint)
        self.features_bias = self.add_weight((self.units,),
                                        name='features_bias',
                                        initializer=self.bias_initializer,
                                        regularizer=self.bias_regularizer,
                                        constraint=self.bias_constraint)
        
        #W_g and b_g
        
        self.recurrent_kernel = self.add_weight(
                                        (self.input_dim+self.units, self.units),
                                        name='recurrent_kernel',
                                        initializer=self.recurrent_initializer,
                                        regularizer=self.recurrent_regularizer,
                                        constraint=self.recurrent_constraint)
        self.recurrent_bias = self.add_weight((self.units,),
                                        name='recurrent_bias',
                                        initializer=self.bias_initializer,
                                        regularizer=self.bias_regularizer,
                                        constraint=self.bias_constraint)
        
        #W_a
        self.average_kernel = self.add_weight(
                                        (self.input_dim+self.units, self.units),
                                        name='average_kernel',
                                        initializer=self.average_initializer,
                                        regularizer=self.average_regularizer,
                                        constraint=self.average_constraint)

        #s
        
        self.initial_attention = self.add_weight((self.units, ),
                                        name='initial_attention',
                                        initializer=self.initial_attention_initializer,
                                        regularizer=self.initial_attention_regularizer,
                                        constraint=self.initial_attention_constraint)

        self.built = True

    def preprocess_input(self, inputs, training=None):
        return inputs
    
    def get_initial_states(self, inputs):
        #states: h, d, n, a_max
        # build an all-zero tensor of shape (samples, output_dim)
        initial_state = K.zeros_like(inputs)  # (samples, timesteps, input_dim)
        initial_state = K.sum(initial_state, axis=(1, 2))  # (samples,)
        initial_state = K.expand_dims(initial_state)  # (samples, 1)
        initial_state = K.tile(initial_state, [1, self.units])  # (samples, output_dim)
        initial_states = [initial_state for _ in range(len(self.states)-1)]
        
        initial_state = K.zeros_like(inputs)  # (samples, timesteps, input_dim)
        initial_state = K.sum(initial_state, axis=(1, 2))  # (samples,)
        initial_state = K.expand_dims(initial_state)  # (samples, 1)
        initial_state = K.tile(initial_state, [1, self.units])
        dtype = initial_state.dtype.name
        min_value = np.asscalar(np.array([1E38]).astype(dtype))
        initial_state = initial_state - min_value
        initial_states.append(initial_state)
        return initial_states
    
    def get_constants(self, inputs, training=None):
        constants = []
        return constants

    def step(self, inputs, states):
        h = states[0]
        d = states[1]
        n = states[2]
        a_max = states[3]
#         dp_mask = states[2]
#         rec_dp_mask = states[3]
        inputs_joined = K.concatenate([inputs, h], axis=-1)
        u = K.dot(inputs,self.features_kernel)
        u = K.bias_add(u, self.features_bias)
        
        g = K.dot(inputs_joined, self.recurrent_kernel)
        g = K.bias_add(g, self.recurrent_bias)
        
        a = K.dot(inputs_joined, self.average_kernel)
        
        z = u * self.recurrent_activation(g)
        
        a_newmax = K.maximum(a_max, a)
        exp_diff = K.exp(a_max - a_newmax)
        exp_scaled = K.exp(a - a_newmax)
        
        n = n*exp_diff + z*exp_scaled
        d = d*exp_diff + exp_scaled
        h_new = self.activation(n/d)
        a_max = a_newmax
        h = h_new

        return h, [h, d, n, a_max]

    def get_config(self):
        config = {'units': self.units,
                  'activation': activations.serialize(self.activation),
                  'recurrent_activation': activations.serialize(self.recurrent_activation),
                  'features_initializer': initializers.serialize(self.features_initializer),
                  'recurrent_initializer': initializers.serialize(self.recurrent_initializer),
                  'average_initializer': initializers.serialize(self.average_initializer),
                  'initial_attention_initializer':  initializers.serialize(self.initial_attention_initializer),
                  'bias_initializer': initializers.serialize(self.bias_initializer),
                  'features_regularizer': regularizers.serialize(self.features_regularizer),
                  'recurrent_regularizer': regularizers.serialize(self.recurrent_regularizer),
                    'average_regularizer': regularizers.serialize(self.average_regularizer),
                    'initial_attention_regularizer': regularizers.serialize(self.initial_attention_regularizer),
                  'bias_regularizer': regularizers.serialize(self.bias_regularizer),
                  'features_constraint': constraints.serialize(self.features_constraint),
                  'recurrent_constraint': constraints.serialize(self.recurrent_constraint),
                  'average_constraint': constraints.serialize(self.average_constraint),
                  'initial_attention_constraint': constraints.serialize(self.initial_attention_constraint),
                  'bias_constraint': constraints.serialize(self.bias_constraint),
#                   'dropout': self.dropout,
#                   'recurrent_dropout': self.recurrent_dropout
                 }
        base_config = super(RWA, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))