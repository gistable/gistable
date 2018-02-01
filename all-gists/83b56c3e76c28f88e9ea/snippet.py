import chainer
import chainer.functions as F
import chainer.optimizers as Opt
import numpy
from sklearn.datasets import fetch_mldata
from libdnn import StackedAutoEncoder


model = chainer.FunctionSet(
    enc1=F.Linear(28 ** 2, 200),
    enc2=F.Linear(200, 30),
    dec2=F.Linear(30, 200),
    dec1=F.Linear(200, 28 ** 2)
)


def encode(self, x, layer, train):
    if train:
        x = F.dropout(x, ratio=0.2, train=train)

    if layer == 0:
        return x

    x = F.sigmoid(self.model.enc1(x))
    if layer == 1:
        return x

    x = F.sigmoid(self.model.enc2(x))
    if layer == 2:
        return x

    return x


def decode(self, x, layer=None, train=False):
    if not train or layer == 2:
        x = F.sigmoid(self.model.dec2(x))

    if not train or layer == 1:
        x = F.sigmoid(self.model.dec1(x))

    return x

sda = StackedAutoEncoder(model, gpu=0)
sda.set_order(('enc1', 'enc2'), ('dec2', 'dec1'))
sda.set_optimizer(Opt.AdaDelta)
sda.set_encode(encode)
sda.set_decode(decode)

mnist = fetch_mldata('MNIST original', data_home='.')
perm = numpy.random.permutation(len(mnist.data))
mnist.data = mnist.data.astype(numpy.float32) / 255
train_data = mnist.data[perm][:60000]
test_data = mnist.data[perm][60000:]

for epoch in range(10):
    print('epoch : %d' % (epoch + 1))
    err = sda.train(train_data, batchsize=200)
    print(err)
    perm = numpy.random.permutation(len(test_data))
    terr = sda.test(test_data[perm][:100])
    print(terr)

    with open('sda.log', mode='a') as f:
        f.write("%d %f %f %f\n" % (epoch + 1, err[0], err[1], terr))

    sda.save_param('sda.param.npy')