import argparse
import numpy as np
from sklearn.datasets import fetch_mldata
from chainer import Variable, FunctionSet, optimizers, cuda
import chainer.functions  as F
#import utils

parser = argparse.ArgumentParser(description='Chainer example: MNIST')
parser.add_argument('--gpu', '-g', default=-1, type=int,
                    help='GPU ID (negative value indicates CPU)')
args = parser.parse_args()

use_gpu = False
if args.gpu >= 0:
    use_gpu = True
    cuda.init(args.gpu)

class Perceptron():
    def __init__(self, n_in, n_out, use_cuda=False):
        self.model = FunctionSet(
            transform=F.Linear(n_in, n_out)
        )
        self.use_cuda = use_cuda

        if self.use_cuda:
            self.model.to_gpu()

        self.optimizer = optimizers.Adam()
        self.optimizer.setup(self.model.collect_parameters())

    def predict(self, x_data):
        x = Variable(x_data)
        y = self.model.transform(x)
        return y.data

    def cost(self, x_data, y_data):
        x = Variable(x_data)
        t = Variable(y_data)
        y = self.model.transform(x)
        return F.softmax_cross_entropy(y, t), F.accuracy(y, t)

    def train(self, x_data, y_data):
        if self.use_cuda:
            x_data = cuda.to_gpu(x_data)
            y_data = cuda.to_gpu(y_data)
        self.optimizer.zero_grads()
        loss, acc = self.cost(x_data, y_data)
        loss.backward()
        self.optimizer.update()
        return float(cuda.to_cpu(loss.data)), float(cuda.to_cpu(acc.data))

    def test(self, x_data, y_data):
        if self.use_cuda:
            x_data = cuda.to_gpu(x_data)
            y_data = cuda.to_gpu(y_data)
        loss, acc = self.cost(x_data, y_data)
        return float(cuda.to_cpu(loss.data)), float(cuda.to_cpu(acc.data))

class DenoisingAutoEncoder():
    def __init__(self, n_in, n_hidden, use_cuda=False):
        self.model = FunctionSet(
            encode=F.Linear(n_in, n_hidden),
            decode=F.Linear(n_hidden, n_in)
        )
        self.use_cuda = use_cuda

        if self.use_cuda:
            self.model.to_gpu()

        self.optimizer = optimizers.Adam()
        self.optimizer.setup(self.model.collect_parameters())

    def encode(self, x_var):
        return F.sigmoid(self.model.encode(x_var))

    def decode(self, x_var):
        return F.sigmoid(self.model.decode(x_var))

    def predict(self, x_data):
        if self.use_cuda:
            x_data = cuda.to_gpu(x_data)
        x = Variable(x_data)
        p = self.encode(x)
        return cuda.to_cpu(p.data)

    def cost(self, x_data):
        x = Variable(x_data)
        t = Variable(x_data)
        x_n = F.dropout(x)
        h = self.encode(x_n)
        y = self.decode(h)
        return F.mean_squared_error(y, t)

    def train(self, x_data):
        if self.use_cuda:
            x_data = cuda.to_gpu(x_data)
        self.optimizer.zero_grads()
        loss = self.cost(x_data)
        loss.backward()
        self.optimizer.update()
        return float(cuda.to_cpu(loss.data))

    def test(self, x_data):
        if self.use_cuda:
            x_data = cuda.to_gpu(x_data)
        loss = self.cost(x_data)
        return float(cuda.to_cpu(loss.data))

#    def visualize(self):
#        if self.use_cuda:
#            self.model.to_cpu()
#        tile_size = (int(np.sqrt(self.model.encode.W[0].size)), int(np.sqrt(self.model.encode.W[0].size)))
#        panel_shape = (10, 10)
#        img = utils.visualize_weights(self.model.encode.W, panel_shape, tile_size)
#        if self.use_cuda:
#            self.model.to_gpu()
#
#        return img

mnist = fetch_mldata('MNIST original')
mnist.data = mnist.data.astype(np.float32)
mnist.data /= 255
mnist.target = mnist.target.astype(np.int32)

batchsize = 100
n_epochs = 50

N = 60000

x_train, x_test = np.split(mnist.data, [N])
y_train, y_test = np.split(mnist.target, [N])
N_test = y_test.size

dae1 = DenoisingAutoEncoder(784, 1000, use_gpu)

for epoch in xrange(n_epochs):
    print "Epoch {}".format(epoch + 1)
    perm = np.random.permutation(N)
    sum_loss = 0
    for i in xrange(0, N, batchsize):
        x_batch = x_train[perm[i:i+batchsize]]
        sum_loss += dae1.train(x_batch) * batchsize

    mean_loss = sum_loss / N
    print "- Layer 1 train mean loss={}".format(mean_loss)

    sum_loss = 0
    for i in xrange(0, N_test, batchsize):
        x_batch = x_test[i:i+batchsize]
        sum_loss += dae1.test(x_batch) * batchsize

    mean_loss = sum_loss / N_test
    print "- Layer 1 test mean loss={}".format(mean_loss)

#img1 = dae1.visualize()
#img1.save("weights1.bmp")

x_train = dae1.predict(x_train)
x_test = dae1.predict(x_test)

dae2 = DenoisingAutoEncoder(1000, 1000, use_gpu)

for epoch in xrange(n_epochs):
    print "Epoch {}".format(epoch + 1)
    perm = np.random.permutation(N)
    sum_loss = 0
    for i in xrange(0, N, batchsize):
        x_batch = x_train[perm[i:i+batchsize]]
        sum_loss += dae2.train(x_batch) * batchsize

    mean_loss = sum_loss / N
    print "- Layer 2 train mean loss={}".format(mean_loss)

    sum_loss = 0
    for i in xrange(0, N_test, batchsize):
        x_batch = x_test[i:i+batchsize]
        sum_loss += dae2.test(x_batch) * batchsize

    mean_loss = sum_loss / N_test
    print "- Layer 2 test mean loss={}".format(mean_loss)

x_train = dae2.predict(x_train)
x_test = dae2.predict(x_test)

dae3 = DenoisingAutoEncoder(1000, 1000, use_gpu)

for epoch in xrange(n_epochs):
    print "Epoch {}".format(epoch + 1)
    perm = np.random.permutation(N)
    sum_loss = 0
    for i in xrange(0, N, batchsize):
        x_batch = x_train[perm[i:i+batchsize]]
        sum_loss += dae3.train(x_batch) * batchsize

    mean_loss = sum_loss / N
    print "- Layer 3 train mean loss={}".format(mean_loss)

    sum_loss = 0
    for i in xrange(0, N_test, batchsize):
        x_batch = x_test[i:i+batchsize]
        sum_loss += dae3.test(x_batch) * batchsize

    mean_loss = sum_loss / N_test
    print "- Layer 3 test mean loss={}".format(mean_loss)


x_train = dae3.predict(x_train)
x_test = dae3.predict(x_test)

classifier = Perceptron(1000, 10, use_gpu)

for epoch in xrange(1000):
    print "Epoch %d" % epoch
    perm = np.random.permutation(N)
    sum_loss = 0
    sum_acc = 0
    for i in xrange(0, N, batchsize):
        x_batch = x_train[perm[i:i+batchsize]]
        y_batch = y_train[perm[i:i+batchsize]]
        loss, acc = classifier.train(x_batch, y_batch)
        sum_loss += loss * batchsize
        sum_acc += acc * batchsize

    mean_loss = sum_loss / N
    mean_acc = sum_acc / N
    print "- Perceptron train mean loss={} accuracy={}".format(mean_loss, mean_acc)

    sum_loss = 0
    sum_acc = 0

    for i in xrange(0, N_test, batchsize):
        x_batch = x_test[i:i+batchsize]
        y_batch = y_test[i:i+batchsize]
        loss, acc = classifier.test(x_batch, y_batch)
        sum_loss += loss * batchsize
        sum_acc += acc * batchsize

    mean_loss = sum_loss / N_test
    mean_acc = sum_acc / N_test
    print "- Perceptron test mean loss={} accuracy={}".format(mean_loss, mean_acc)
