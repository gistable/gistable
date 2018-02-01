from keras.engine.topology import Layer
from keras import initializations
from keras import backend as K

class Attention(Layer):
    '''Attention operation for temporal data.
    # Input shape
        3D tensor with shape: `(samples, steps, features)`.
    # Output shape
        2D tensor with shape: `(samples, features)`.
    '''
    def __init__(self, attention_dim, **kwargs):
        self.init = initializations.get('glorot_uniform')
        self.attention_dim = attention_dim
        super(Attention, self).__init__(**kwargs)

    def build(self, input_shape):
        self.W = self.init((self.attention_dim, self.attention_dim),
                           name='{}_W'.format(self.name))
        self.b = K.zeros((self.attention_dim,), name='{}_b'.format(self.name))
        self.u = self.init((self.attention_dim,), name='{}_u'.format(self.name))
        self.trainable_weights += [self.W, self.b, self.u]
        self.built = True
         
    def get_output_shape_for(self, input_shape):
        return (input_shape[0], input_shape[2])

    def call(self, x, mask=None):
        # Calculate the first hidden activations
        a1 = K.tanh(K.dot(x, self.W) + self.b) # [n_samples, n_steps, n_hidden]
        # K.dot won't let us dot a 3D with a 1D so we do it with mult + sum
        mul_a1_u = a1 * self.u                  # [n_samples, n_steps, n_hidden]
        dot_a1_u = K.sum(mul_a1_u, axis=2)      # [n_samples, n_steps]
        # Calculate the per step attention weights
        a2 = K.softmax(dot_a1_u)
        a2 = K.expand_dims(a2)                  # [n_samples, n_steps, 1] so div broadcasts
        # Apply attention weights to steps
        weighted_input = x * a2                 # [n_samples, n_steps, n_features]
        # Sum across the weighted steps to get the pooled activations
        return K.sum(weighted_input, axis=1)