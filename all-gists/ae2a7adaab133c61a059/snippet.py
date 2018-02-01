import lasagne as nn
Conv2DLayer = nn.layers.Conv2DDNNLayer

def inception_module(l_in, num_1x1, reduce_3x3, num_3x3, reduce_5x5, num_5x5, gain=1.0, bias=0.1):
    """
    inception module (without the 3x3s1 pooling and projection because that's difficult in Theano right now)
    """
    shape = l_in.get_output_shape()
    out_layers = []

    # 1x1
    if num_1x1 > 0:
        l_1x1 = nn.layers.NINLayer(l_in, num_units=num_1x1, W=nn.init.Orthogonal(gain), b=nn.init.Constant(bias))
        out_layers.append(l_1x1)
    
    # 3x3
    if num_3x3 > 0:
        if reduce_3x3 > 0:
            l_reduce_3x3 = nn.layers.NINLayer(l_in, num_units=reduce_3x3, W=nn.init.Orthogonal(gain), b=nn.init.Constant(bias))
        else:
            l_reduce_3x3 = l_in
        l_3x3 = Conv2DLayer(l_reduce_3x3, num_filters=num_3x3, filter_size=(3, 3), border_mode="same", W=nn.init.Orthogonal(gain), b=nn.init.Constant(bias))
        out_layers.append(l_3x3)
    
    # 5x5
    if num_5x5 > 0:
        if reduce_5x5 > 0:
            l_reduce_5x5 = nn.layers.NINLayer(l_in, num_units=reduce_5x5, W=nn.init.Orthogonal(gain), b=nn.init.Constant(bias))
        else:
            l_reduce_5x5 = l_in
        l_5x5 = Conv2DLayer(l_reduce_5x5, num_filters=num_5x5, filter_size=(5, 5), border_mode="same", W=nn.init.Orthogonal(gain), b=nn.init.Constant(bias))
        out_layers.append(l_5x5)
    
    # stack
    l_out = nn.layers.concat(out_layers)
    return l_out