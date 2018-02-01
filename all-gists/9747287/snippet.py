import theano
from pylearn2.models import mlp
from pylearn2.train_extensions import best_params
from pylearn2.training_algorithms import sgd, learning_rule
from pylearn2.utils import serial
from pylearn2.termination_criteria import MonitorBased
from pylearn2.datasets.dense_design_matrix import DenseDesignMatrix
from sklearn.preprocessing import StandardScaler
import numpy as np
from random import randint
import itertools
import os

os.system('rm /tmp/best.pkl')

PIMA_DATASET = './pima-indians-diabetes.data'
 
scaler = StandardScaler()

class Pima(DenseDesignMatrix):
    def __init__(self, X=None, y=None):
        X = X
        y = y
        if X is None:
            X = []
            y = []
            with open(PIMA_DATASET) as f:
                for line in f:
                    features, label = line.rsplit(',', 1)
                    X.append(map(float, features.split(',')))
                    if int(label) == 0:
                        y.append([1, 0])
                    else:
                        y.append([0, 1])
            X = np.asarray(X)
            X = scaler.fit_transform(X)
            y = np.asarray(y)
        super(Pima, self).__init__(X=X, y=y)

    @property
    def nr_inputs(self):
        return len(self.X[0])

    def split(self, prop=.8):
        cutoff = int(len(self.y) * prop)
        X1, X2 = self.X[:cutoff], self.X[cutoff:]
        y1, y2 = self.y[:cutoff], self.y[cutoff:]
        return Pima(X1, y1), Pima(X2, y2)

    def __len__(self):
        return self.X.shape[0]

    def __iter__(self):
        return itertools.izip_longest(self.X, self.y)
    

# create datasets
ds_train = Pima()
ds_train, ds_valid = ds_train.split(0.7)
ds_valid, ds_test = ds_valid.split(0.7)

# create sigmoid hidden layer with 20 nodes, init weights in range -0.05 to 0.05 and add
# a bias with value 1
hidden_layer = mlp.Sigmoid(layer_name='hidden', dim=20, irange=.05, init_bias=1.)
# softmax output layer
output_layer = mlp.Softmax(2, 'output', irange=.05)
layers = [hidden_layer, output_layer]

# termination criterion that stops after 50 epochs without
# any increase in misclassification on the validation set
termination_criterion = MonitorBased(channel_name='output_misclass',
                                     N=50, prop_decrease=0.0)

# momentum
initial_momentum = .5
final_momentum = .99
start = 1
saturate = 50
momentum_adjustor = learning_rule.MomentumAdjustor(final_momentum, start, saturate)
momentum_rule = learning_rule.Momentum(initial_momentum)

# learning rate
start = 1
saturate = 50
decay_factor = .1
learning_rate_adjustor = sgd.LinearDecayOverEpoch(start, saturate, decay_factor)

# create neural net
ann = mlp.MLP(layers, nvis=ds_train.nr_inputs)

# create Stochastic Gradient Descent trainer 
trainer = sgd.SGD(learning_rate=.05, batch_size=10, monitoring_dataset=ds_valid,
                  termination_criterion=termination_criterion, learning_rule=momentum_rule)
trainer.setup(ann, ds_train)

# add monitor for saving the model with best score
monitor_save_best = best_params.MonitorBasedSaveBest('output_misclass',
                                                     '/tmp/best.pkl')

# train neural net until the termination criterion is true
while True:
    trainer.train(dataset=ds_train)
    ann.monitor.report_epoch()
    ann.monitor()
    monitor_save_best.on_monitor(ann, ds_valid, trainer)
    if not trainer.continue_learning(ann):
        break
    momentum_adjustor.on_monitor(ann, ds_valid, trainer)
    learning_rate_adjustor.on_monitor(ann, ds_valid, trainer)

# load the best model
ann = serial.load('/tmp/best.pkl')

# function for classifying a input vector
def classify(inp):
    inp = np.asarray(inp)
    inp.shape = (1, ds_train.nr_inputs)
    return np.argmax(ann.fprop(theano.shared(inp, name='inputs')).eval())

# function for calculating and printing the models accuracy on a given dataset
def score(dataset):
    nr_correct = 0
    for features, label in dataset:
        if classify(features) == np.argmax(label):
            nr_correct += 1
    print '%s/%s correct' % (nr_correct, len(dataset))

print
print 'Accuracy of train set:'
score(ds_train)
print 'Accuracy of validation set:'
score(ds_valid)
print 'Accuracy of test set:'
score(ds_test)
