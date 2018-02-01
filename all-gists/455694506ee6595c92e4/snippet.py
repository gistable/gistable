import argparse
import numpy as np
from sklearn.datasets import fetch_mldata
from chainer import Variable, FunctionSet, optimizers, cuda
import chainer.functions  as F
import brica1

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
        if self.use_cuda:
            x_data = cuda.to_gpu(x_data)
        x = Variable(x_data)
        y = F.softmax(self.model.transform(x))
        return cuda.to_cpu(y.data)

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

class DenoisingAutoencoder():
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

class MNISTSensor(brica1.Component):
    def __init__(self, N_train=60000, batchsize=100):
        super(MNISTSensor, self).__init__()
        mnist = fetch_mldata('MNIST original')
        mnist.data = mnist.data.astype(np.float32)
        mnist.data /= 255
        mnist.target = mnist.target.astype(np.int32)

        _, x_dim = mnist.data.shape
        y_dim = 1

        x_train, x_test = np.split(mnist.data, [N_train])
        y_train, y_test = np.split(mnist.target, [N_train])
        N_test = y_test.size

        self.x_train = x_train
        self.y_train = y_train
        self.x_test = x_test
        self.y_test = y_test
        self.N_train = N_train
        self.N_test = N_test
        self.i_train = 0
        self.i_test = 0
        self.batchsize = batchsize

        self.make_out_port("x_train", x_dim)
        self.make_out_port("y_train", y_dim)
        self.make_out_port("x_test", x_dim)
        self.make_out_port("y_test", y_dim)

        self.set_out_port("x_train", brica1.Port(np.zeros((x_dim, 1), dtype=np.float32)))
        self.set_out_port("x_test", brica1.Port(np.zeros((x_dim, 1), dtype=np.float32)))

        self.fire()
        self.output(0.0)

    def fire(self):
        if self.i_train == 0:
            perm = np.random.permutation(self.N_train)
            self.x_train = self.x_train[perm]
            self.y_train = self.y_train[perm]

        x_train_batch = self.x_train[self.i_train:self.i_train+self.batchsize]
        y_train_batch = self.y_train[self.i_train:self.i_train+self.batchsize]
        x_test_batch = self.x_test[self.i_test:self.i_test+self.batchsize]
        y_test_batch = self.y_test[self.i_test:self.i_test+self.batchsize]

        self.results["x_train"] = x_train_batch
        self.results["y_train"] = y_train_batch
        self.results["x_test"] = x_test_batch
        self.results["y_test"] = y_test_batch

        self.i_train = (self.i_train + self.batchsize) % self.N_train
        self.i_test = (self.i_test + self.batchsize) % self.N_test

class DAComponent(brica1.Component):
    def __init__(self, n_in, n_hidden, min_loss=0.001, max_cycles=100000, use_cuda=False):
        super(DAComponent, self).__init__()
        self.dA = DenoisingAutoencoder(n_in, n_hidden, use_cuda=use_cuda)
        self.n_in = n_in
        self.n_hidden = n_hidden
        self.make_in_port("in", n_in)
        self.make_out_port("out", n_hidden)
        self.min_loss = min_loss
        self.max_cycles = max_cycles
        self.train = True
        self.loss = 999.0
        self.cycle = 0

    def fire(self):
        x_train = self.inputs["in"]

        if len(x_train.shape) != 2:
            return

        M, N = x_train.shape

        if N != self.n_in:
            return

        if self.train:
            self.loss = self.dA.train(self.inputs["in"])
            self.cycle += 1

            if self.loss <= self.min_loss:
                self.train = False

            if self.max_cycles <= self.cycle:
                self.train = False

        self.results["out"] = self.dA.predict(x_train)

class PerceptronComponent(brica1.Component):
    def __init__(self, n_in, n_out, min_loss=0.001, max_cycles=1000000, use_cuda=False):
        super(PerceptronComponent, self).__init__()
        self.perceptron = Perceptron(n_in, n_out, use_cuda=use_cuda)
        self.n_in = n_in
        self.n_out = n_out
        self.make_in_port("x_in", n_in)
        self.make_in_port("y_in", n_in)
        self.make_out_port("out", n_out)
        self.min_loss = min_loss
        self.max_cycles = max_cycles
        self.train = True
        self.loss = 999.0
        self.acc = 0.0
        self.cycle = 0

    def fire(self):
        x_train = self.inputs["x_in"]
        y_train = self.inputs["y_in"]

        if len(x_train.shape) != 2:
            return

        M, N = x_train.shape

        if N != self.n_in:
            return

        if self.train:
            loss, acc = self.perceptron.train(x_train, y_train)
            self.loss = loss
            self.acc = acc
            self.cycle += 1

            if self.loss <= self.min_loss:
                self.train = False

            if self.max_cycles <= self.cycle:
                self.train = False

        self.results["out"] = self.perceptron.predict(x_train)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SdA with Chainer + BriCA')
    parser.add_argument('--gpu', '-g', default=-1, type=int,
                        help='GPU ID (negative value indicates CPU)')
    args = parser.parse_args()

    use_gpu = False
    if args.gpu >= 0:
        use_gpu = True
        cuda.init(args.gpu)

    s = brica1.VirtualTimeScheduler()
    ca = brica1.Agent(s)

    cycles = 24000
    sensor = MNISTSensor()
    da1 = DAComponent(784, 1000, use_cuda=use_gpu, max_cycles=cycles)
    da2 = DAComponent(1000, 1000, use_cuda=use_gpu, max_cycles=cycles)
    da3 = DAComponent(1000, 1000, use_cuda=use_gpu, max_cycles=cycles)
    perceptron = PerceptronComponent(1000, 10, use_cuda=use_gpu, max_cycles=cycles)

    sda = brica1.ComponentSet()
    brica1.connect((da1, "out"), (da2, "in"))
    brica1.connect((da2, "out"), (da3, "in"))
    sda.add_component("da1", da1, 0)
    sda.add_component("da2", da2, 1)
    sda.add_component("da3", da3, 2)
    sda.make_in_port("x_in", 784)
    sda.make_in_port("y_in", 1)
    sda.make_out_port("out", 1)

    brica1.connect((sensor, "x_train"), (da1, "in"))
    brica1.connect((da1, "out"), (da2, "in"))
    brica1.connect((da2, "out"), (da3, "in"))
    brica1.connect((da3, "out"), (perceptron, "x_in"))
    brica1.connect((sensor, "y_train"), (perceptron, "y_in"))

    sda = brica1.ComponentSet()
    sda.make_out_port("out", 1)
    sda.add_component("sensor", sensor, 0)
    sda.add_component("da1", da1, 1)
    sda.add_component("da2", da2, 2)
    sda.add_component("da3", da3, 3)
    sda.add_component("perceptron", perceptron, 4)
    brica1.alias_out_port((sda, "out"), (perceptron, "out"))

    mod = brica1.Module()
    mod.make_out_port("out", 1)
    mod.add_component("sda", sda)
    brica1.alias_out_port((mod, "out"), (sda, "out"))

    ca.add_submodule("mod", mod)

    epoch = 0
    while perceptron.train:
        da1_sum = 0
        da2_sum = 0
        da3_sum = 0
        acc_sum = 0
        for i in xrange(600):
            time = ca.step()
            da1_sum += da1.loss
            da2_sum += da2.loss
            da3_sum += da3.loss
            acc_sum += perceptron.acc
            if (int(time) + 1) % 100 == 0:
                print "Time {:}: L1={:.5f} L2={:.5f} L3={:.5f} Acc={:.5f}".format(time+1, da1.loss, da2.loss, da3.loss, perceptron.acc)

        epoch += 1
        da1_avg = da1_sum / 600
        da2_avg = da2_sum / 600
        da3_avg = da3_sum / 600
        acc_avg = acc_sum / 600

        print "Epoch {:}: L1={:.5f} L2={:.5f} L3={:.5f} Acc={:.5f}".format(epoch, da1_avg, da2_avg, da3_avg, acc_avg)