from keras import backend as K
from keras.layers.recurrent import LSTM

class HiddenStateLSTM(LSTM):
    """LSTM with input/output capabilities for its hidden state.

    This layer behaves just like an LSTM, except that it accepts further inputs
    to be used as its initial states, and returns additional outputs,
    representing the layer's final states.

    See Also:
        https://github.com/fchollet/keras/issues/2995
    """
    def build(self, input_shape):
        if isinstance(input_shape, list) and len(input_shape) > 1:
            input_shape, *hidden_shapes = input_shape
            for shape in hidden_shapes:
                assert shape[0]  == input_shape[0]
                assert shape[-1] == self.output_dim
        super().build(input_shape)

    def call(self, x, mask=None):
        # input shape: (nb_samples, time (padded with zeros), input_dim)
        input_shape = self.input_spec[0].shape
        if isinstance(x, (tuple, list)):
            x, *custom_initial = x
        else:
            custom_initial = None
        if K._BACKEND == 'tensorflow':
            if not input_shape[1]:
                raise Exception('When using TensorFlow, you should define '
                                'explicitly the number of timesteps of '
                                'your sequences.\n'
                                'If your first layer is an Embedding, '
                                'make sure to pass it an "input_length" '
                                'argument. Otherwise, make sure '
                                'the first layer has '
                                'an "input_shape" or "batch_input_shape" '
                                'argument, including the time axis. '
                                'Found input shape at layer ' + self.name +
                                ': ' + str(input_shape))
        if self.stateful and custom_initial:
            raise Exception(('Initial states should not be specified '
                             'for stateful LSTMs, since they would overwrite '
                             'the memorized states.'))
        elif custom_initial:
            initial_states = custom_initial
        elif self.stateful:
            initial_states = self.states
        else:
            initial_states = self.get_initial_states(x)
        constants = self.get_constants(x)
        preprocessed_input = self.preprocess_input(x)

        # only use the main input mask
        if isinstance(mask, list):
            mask = mask[0]

        last_output, outputs, states = K.rnn(self.step, preprocessed_input,
                                             initial_states,
                                             go_backwards=self.go_backwards,
                                             mask=mask,
                                             constants=constants,
                                             unroll=self.unroll,
                                             input_length=input_shape[1])
        if self.stateful:
            self.updates = []
            for i in range(len(states)):
                self.updates.append((self.states[i], states[i]))

        if self.return_sequences:
            return [outputs] + states
        else:
            return [last_output] + states

    def get_output_shape_for(self, input_shape):
        if isinstance(input_shape, list) and len(input_shape) > 1:
            input_shape = input_shape[0]
        if self.return_sequences:
            output_shape = (input_shape[0], input_shape[1], self.output_dim)
        else:
            output_shape = (input_shape[0], self.output_dim)
        state_output = (input_shape[0], self.output_dim)
        return [output_shape, state_output, state_output]

    def compute_mask(self, input, mask):
        if isinstance(mask, list) and len(mask) > 1:
            return mask
        elif self.return_sequences:
            return [mask, None, None]
        else:
            return [None] * 3

#####################
### Usage example ###
#####################

if __name__ == '__main__':
  from keras.layers import Input, Embedding, Dense, TimeDistributed, Activation
  from keras.models import Model

  ### build encoder
  enc_input = Input(shape=(24,), dtype='int32', name='encoder_input')
  enc_layer = Embedding(128, 64, mask_zero=True)(enc_input)
  enc_layer, *hidden = HiddenStateLSTM(64, dropout_W=0.5, return_sequences=False)(enc_layer)

  ### build decoder
  dec_input = Input(shape=(24,), dtype='int32', name='decoder_input')
  dec_layer = Embedding(128, 64, mask_zero=True)(dec_input)
  dec_layer, _, _ = HiddenStateLSTM(64, dropout_W=0.5, return_sequences=True)([dec_layer] + hidden)
  dec_layer = TimeDistributed(Dense(128))(dec_layer)
  dec_output = Activation('softmax', name='decoder_output')(dec_layer)

  ### build model
  model = Model(input=[enc_input, dec_input], output=dec_output)
  model.compile(optimizer='adam', loss='categorical_crossentropy')
