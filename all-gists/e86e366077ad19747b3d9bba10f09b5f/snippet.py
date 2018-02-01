class OloloLayer(Layer):
    def __init__(self, w, k, **kwargs):
        self.w = w
        self.k = k
        return super(OloloLayer, self).__init__(**kwargs)

    def call(self, x, mask=None):
        w = self.w
        x_coords = K.reshape(K.concatenate([K.one_hot([i, j], w) for i in range(w) for j in range(w)], 0), (1, w, w, w*2))
        x_coords = tf.tile(x_coords, [K.shape(x)[0], 1, 1, 1])
        x = K.concatenate([x, x_coords])
        return x_coords

    def get_config(self):
        base_config = super(OloloLayer, self).get_config()
        return base_config


    def get_output_shape_for(self, input_shape):
        return (input_shape[0], self.w*self.w*(self.w*self.w-1)/2, (self.k+self.w*2)*2) 