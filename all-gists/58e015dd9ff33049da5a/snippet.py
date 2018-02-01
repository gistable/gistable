import argparse
import numpy as np
from chainer import Variable, FunctionSet, optimizers, cuda
import chainer.functions  as F
import cv2
import random
import cPickle as pickle
import sys

class ConvolutionalAutoencoder(FunctionSet):
    def __init__(self, n_in, n_out, ksize, stride=1, pad=0, wscale=1, bias=0, nobias=False):
        super(ConvolutionalAutoencoder, self).__init__(
            encode=F.Convolution2D(n_in, n_out, ksize, stride=stride, pad=pad, wscale=wscale, bias=bias, nobias=nobias),
            decode=F.Convolution2D(n_out, n_in, ksize, stride=stride, pad=pad, wscale=wscale, bias=bias, nobias=nobias)
        )

    def forward(self, x_data, y_data, train=True):
        x = Variable(x_data)
        t = Variable(x_data)
        if train:
            x = F.dropout(x)
        h = F.sigmoid(self.encode(x))
        y = F.sigmoid(self.decode(h))
        return F.mean_squared_error(y, t)

class Trainer():
    def __init__(self, model, optimizer, loader, min_loss=None, max_epochs=10, logger=None):
        self.model = model
        self.optimizer = optimizer
        self.optimizer.setup(model.collect_parameters())
        self.loader = loader
        self.min_loss = min_loss
        self.max_epochs = max_epochs
        self.logger = logger

    def train(self, batchnum, batchsize):
        self.optimizer.zero_grads()
        x_data, y_data = self.loader(batchnum, batchsize)
        loss = self.model.forward(x_data, y_data, train=True)
        loss.backward()
        self.optimizer.update()
        return loss.data

    def loop(self, N, batchsize):
        for epoch in xrange(self.max_epochs):
            for batchnum in xrange(N / batchsize):
                loss = float(cuda.to_cpu(self.train(batchnum, batchsize)))

                if not self.logger == None:
                    logger(epoch+1, batchnum+1, loss)

                if not self.min_loss == None:
                    if loss <= self.min_loss:
                        return

def load_image_list(path):
    tuples = []
    for line in open(path):
        pair = line.strip().split()
        tuples.append((pair[0], np.int32(pair[1])))
    return tuples

def compute(x_data, function):
    x = Variable(x_data)
    return function(x).data

def converter_generator(functions=[]):
    def converter(x_data):
        for function in functions:
            x_data = compute(x_data, function)
        return x_data

    return converter

def read_image(path, insize, mean_image, center=False, flip=False):
    cropwidth = 256 - insize
    image = cv2.imread(path).transpose(2, 0, 1)
    if center:
        top = left = cropwidth / 2
    else:
        top  = random.randint(0, cropwidth - 1)
        left = random.randint(0, cropwidth - 1)
    bottom = insize + top
    right  = insize + left

    image  = image[[2, 1, 0], top:bottom, left:right].astype(np.float32)
    image -= mean_image[:, top:bottom, left:right]
    image /= 255
    if flip and random.randint(0, 1) == 0:
        return image[:, :, ::-1]
    else:
        return image

def loader_generator(insize, data, mean_image, converter, use_gpu=False):
    insize = 224
    cropwidth = 256 - insize

    perm = np.random.permutation(len(train_list))
    def loader(batchnum, batchsize):
        x_batch = np.ndarray((batchsize, 3, insize, insize), dtype=np.float32)
        y_batch = np.ndarray((batchsize,), dtype=np.int32)

        for i in xrange(batchsize):
            path, label = data[perm[(batchnum * batchsize + i) % len(data)]]
            x_batch[i] = read_image(path, insize, mean_image, False, True)
            y_batch[i] = label

        if use_gpu:
            x_batch = cuda.to_gpu(x_batch)
            y_batch = cuda.to_gpu(y_batch)

        return converter(x_batch), y_batch

    return loader

def logger(epoch, batchnum, loss):
    print 'Epoch {0:d} Batchnum {1:d} Loss={2:.5f}'.format(epoch, batchnum, loss)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Chainer example: Convolutional Autoencoder')
    parser.add_argument('--gpu', '-g', default=-1, type=int,
                        help='GPU ID (negative value indicates CPU)')
    parser.add_argument('--batchsize', '-B', type=int, default=32,
                        help='Learning minibatch size')
    parser.add_argument('--train', '-t', type=str, default="train.txt",
                        help='Training image/label list')
    parser.add_argument('--val', '-v', type=str, default="val.txt",
                        help='Validation image/label list')
    parser.add_argument('--mean', '-m', type=str, default='ilsvrc_2012_mean.npy',
                        help='Image mean file')
    parser.add_argument('--conv1_1', type=str, default=None,
                        help='Pickle file for conv1_1')
    args = parser.parse_args()

    conv1_1 = ConvolutionalAutoencoder( 3, 64, 3, pad=1)

    use_gpu = False
    if args.gpu >= 0:
        use_gpu = True
        cuda.init(args.gpu)
        conv1_1.to_gpu()

    insize = 224
    train_list = load_image_list(args.train)
    val_list = load_image_list(args.val)
    mean_image = np.load(args.mean)
    encoders = []
    decoders = []

    # Train layer 1
    if args.conv1_1 == None:
        converter1_1 = converter_generator(encoders)
        loader1_1 = loader_generator(insize, train_list, mean_image, converter1_1, use_gpu=use_gpu)
        optimizer1_1 = optimizers.MomentumSGD(lr=0.01, momentum=0.9)
        trainer1_1 = Trainer(conv1_1, optimizer1_1, loader1_1, max_epochs=1, logger=logger)

        trainer1_1.loop(len(train_list), args.batchsize)

        f1_1 = open('pkl/conv1_1.pkl', 'wb')
        pickle.dump(conv1_1, f1_1)
        f1_1.close()
    else:
        f1_1 = open(args.conv1_1, 'rb')
        conv1_1 = pickle.load(f1_1)
        f1_1.close()

    encoders = encoders + [conv1_1.encode, F.sigmoid]
    decoders = [conv1_1.decode, F.sigmoid] + decoders
    reconstructor = converter_generator(encoders + decoders)

    path, label = val_list[0]
    x_data = np.ndarray((1, 3, insize, insize), dtype=np.float32)
    x_data[0] = read_image(path, insize, mean_image)
    if use_gpu:
        x_data = cuda.to_gpu(x_data)
    y_data = cuda.to_cpu(reconstructor(x_data))
    x_data = cuda.to_cpu(x_data)

    origin = cv2.cvtColor(x_data[0].transpose(1, 2, 0) * 255, cv2.COLOR_RGB2BGR)
    img1_1 = cv2.cvtColor(y_data[0].transpose(1, 2, 0) * 255, cv2.COLOR_RGB2BGR)
    cv2.imwrite('img/origin.jpg', origin)
    cv2.imwrite('img/img1_1.jpg', img1_1)