from lasagne.layers import Layer

class HighwayLayer(Layer):
    def __init__(self, incoming, layer_class, gate_nonlinearity=None,
                 **kwargs):
        super(HighwayLayer, self).__init__(incoming)

        self.H_layer = layer_class(incoming, **kwargs)
        
        if gate_nonlinearity:
            kwargs['nonlinearity'] = gate_nonlinearity
        else:
            kwargs['nonlinearity'] = lasagne.nonlinearities.sigmoid
        kwargs['b'] = lasagne.init.Constant(-2)
        self.T_layer = layer_class(incoming, **kwargs)
        
    def get_params(self):
        return self.H_layer.get_params() + self.T_layer.get_params()

    def get_bias_params(self):
        return self.H_layer.get_bias_params() + self.T_layer.get_bias_params()

    def get_output_shape_for(self, input_shape):
        return input_shape

    def get_output_for(self, input, **kwargs):
        T = self.T_layer.get_output_for(input, **kwargs)
        return input * (1 - T) + T * self.H_layer.get_output_for(input, **kwargs)


def build_model(input_dim, output_dim,
                batch_size=BATCH_SIZE, num_hidden_units=NUM_HIDDEN_UNITS):
    """ Example usage (replaces build_model in mnist.py) """
    l_in = lasagne.layers.InputLayer(
        shape=(batch_size, input_dim),
    )
    
    l_in = lasagne.layers.DenseLayer(
        l_in,
        num_units=num_hidden_units,
        nonlinearity=lasagne.nonlinearities.rectify,
        W=lasagne.init.HeNormal(),
    )
    
    for i in range(49):
        l_in = HighwayLayer(
            l_in,
            lasagne.layers.DenseLayer,
            num_units=num_hidden_units,
            nonlinearity=lasagne.nonlinearities.rectify,
            W=lasagne.init.HeNormal(),
        )
        
    l_out = lasagne.layers.DenseLayer(
        l_in,
        num_units=output_dim,
        nonlinearity=lasagne.nonlinearities.softmax,
    )
    return l_out