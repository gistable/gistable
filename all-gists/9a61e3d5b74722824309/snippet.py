class ConvolutionalAutoencoder(FunctionSet):
    def __init__(self, n_in, n_out, ksize, stride=1, pad=0, wscale=1, bias=0, nobias=False):
        super(ConvolutionalAutoencoder, self).__init__(
            encode=F.Convolution2D(n_in, n_out, ksize, stride=stride, pad=pad, wscale=wscale, bias=bias, nobias=nobias),
            decode=F.Convolution2D(n_out, n_in, ksize, stride=stride, pad=pad, wscale=wscale, bias=bias, nobias=nobias)
        )

    def forward(self, x_data, train=True):
        x = Variable(x_data)
        t = Variable(x_data)
        if train:
            x = F.dropout(x)
        h = F.sigmoid(self.encode(x))
        y = F.sigmoid(self.decode(h))
        return F.mean_squared_error(y, t)

    def encode(self, x_data):
        x = Variable(x_data)
        h = F.sigmoid(self.encode(x))
        return h.data

    def decode(self, h_data):
        h = Variable(h_data)
        y = F.sigmoid(self.decode(h))
        return y