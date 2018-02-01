import weakref
import matplotlib.pyplot as plt
import numpy
from sklearn.datasets import fetch_mldata


class Variable(object):

    def __init__(self, data):
        self.data = data
        self.grad = None
        self.creator = None

    def set_creator(self, func):
        self.creator = func

    def backward(self):
        if self.data.size == 1 and self.grad is None:
            self.grad = numpy.ones_like(self.data)
        funcs = [self.creator]
        while funcs:
            func = funcs.pop()
            in_data = [x.data for x in func.inputs]
            out_grad = [y().grad for y in func.outputs]
            gxs = func.backward(in_data, out_grad)
            for x, gx in zip(func.inputs, gxs):
                if gx is None:
                    continue
                x.grad = gx
                if x.creator is not None:
                    funcs.append(x.creator)

class Function(object):

    def __call__(self, inputs):
        in_data = [x.data for x in inputs]
        outputs = self.forward(in_data)
        ret = [Variable(y) for y in outputs]
        for y in ret:
            y.set_creator(self)
        self.inputs = inputs
        self.outputs = tuple([weakref.ref(y) for y in ret])
        return ret

    def forward(self, in_data):
        raise NotImplementedError

    def backward(self, in_data, grad_output):
        raise NotImplementedError

class LinearFunction(Function):

    def forward(self, inputs):
        x, W, b = inputs
        return x.dot(W.T) + b,

    def backward(self, inputs, grad_outputs):
        x, W, b = inputs
        gy, = grad_outputs
        gx = gy.dot(W)
        gW = gy.T.dot(x)
        gb = gy.sum(axis=0)
        return gx, gW, gb

class ReLUFunction(Function):

    def forward(self, inputs):
        x, = inputs
        return numpy.maximum(0, x),

    def backward(self, inputs, grad_outputs):
        x, = inputs
        gy, = grad_outputs
        return (x > 0) * gy,

def relu(x):
    return ReLUFunction()((x,))[0]

class Link(object):

    def __init__(self, **params):
        for name, param in params.items():
            setattr(self, name, Variable(param))

    def params(self):
        for param in self.__dict__.values():
            yield param

class Linear(Link):

    def __init__(self, n_in, n_out):
        W = numpy.random.randn(n_out, n_in) * numpy.sqrt(2 / n_in)
        b = numpy.zeros((n_out,))
        super().__init__(W=W, b=b)

    def __call__(self, x):
        return LinearFunction()((x, self.W, self.b))[0]

class Chain(Link):

    def __init__(self, **links):
        super().__init__()
        for name, link in links.items():
            self.__dict__[name] = link

    def params(self):
        for link in self.__dict__.values():
            for param in link.params():
                yield param

class MeanSquaredError(Function):

    def forward(self, inputs):
        x0, x1 = inputs
        return numpy.mean((x0 - x1) ** 2),

    def backward(self, inputs, grad_outputs):
        x0, x1 = inputs
        gy, = grad_outputs
        gx0 = gy * (2. / x0.size) * (x0 - x1)
        return gx0, -gx0

def mean_squared_error(x0, x1):
    return MeanSquaredError()((x0, x1))[0]

class Optimizer(object):

    def setup(self, link):
        self.target = link

    def update(self):
        for param in self.target.params():
            self.update_one(param)

class SGD(Optimizer):

    def __init__(self, lr=0.01):
        self.lr = lr

    def update_one(self, param):
        param.data -= self.lr * param.grad

model = Chain(
    f1=Linear(784, 100),
    f2=Linear(100, 10),
)

def forward(x):
    h = relu(model.f1(x))
    return model.f2(h)

optimizer = SGD(lr=0.01)
optimizer.setup(model)

mnist = fetch_mldata('MNIST original', data_home='./')

x, t = mnist['data'] / 255, mnist['target']
t = numpy.array([t == i for i in range(10)]).T
train_x, train_t = x[:60000], t[:60000]
val_x, val_t = x[60000:], t[60000:]

losses, accuracy = [], []
for epoch in range(150):
    idx = numpy.random.permutation(numpy.arange(len(train_x)))
    train_x = train_x[idx]
    train_t = train_t[idx]
    epoch_loss = []
    for i in range(0, len(train_x), 128):
        batch_x = Variable(train_x[i:i + 128])
        batch_t = Variable(train_t[i:i + 128])
        y = forward(batch_x)
        loss = mean_squared_error(y, batch_t)
        loss.backward()
        optimizer.update()
        epoch_loss.append(loss.data)

    losses.append(numpy.mean(epoch_loss))
    y = forward(Variable(val_x))
    y = numpy.argmax(y.data, axis=1)
    t = numpy.argmax(val_t, axis=1)
    acc = numpy.sum(y == t) / len(y)
    print('epoch:', epoch, 'loss:', loss.data, 'accuracy:', acc)
    accuracy.append(acc)

plt.plot(losses)
plt.title('training loss')
plt.xlabel('epoch')
plt.ylabel('mean squared error')
plt.savefig('loss.png')
plt.clf()
plt.plot(accuracy)
plt.title('validation accuracy')
plt.xlabel('epoch')
plt.ylabel('validation accuracy (%)')
plt.savefig('accuracy.png')
