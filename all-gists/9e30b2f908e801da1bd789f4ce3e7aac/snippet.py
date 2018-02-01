# Drawn from https://gist.github.com/rocknrollnerd/c5af642cf217971d93f499e8f70fcb72 (in Theano)
# This is implemented in PyTorch
# Author : Anirudh Vemula

import torch
import torch.nn as nn
from torch.autograd import Variable
import numpy as np

from sklearn.datasets import fetch_mldata
from sklearn.cross_validation import train_test_split
from sklearn import preprocessing


def log_gaussian(x, mu, sigma):
    return float(-0.5 * np.log(2 * np.pi) - np.log(np.abs(sigma))) - (x - mu)**2 / (2 * sigma**2)


def log_gaussian_logsigma(x, mu, logsigma):
    return float(-0.5 * np.log(2 * np.pi)) - logsigma - (x - mu)**2 / (2 * torch.exp(logsigma)**2)


class MLPLayer(nn.Module):
    def __init__(self, n_input, n_output, sigma_prior):
        super(MLPLayer, self).__init__()
        self.n_input = n_input
        self.n_output = n_output
        self.sigma_prior = sigma_prior
        self.W_mu = nn.Parameter(torch.Tensor(n_input, n_output).normal_(0, 0.01))
        self.W_logsigma = nn.Parameter(torch.Tensor(n_input, n_output).normal_(0, 0.01))
        self.b_mu = nn.Parameter(torch.Tensor(n_output).uniform_(-0.01, 0.01))
        self.b_logsigma = nn.Parameter(torch.Tensor(n_output).uniform_(-0.01, 0.01))
        self.lpw = 0
        self.lqw = 0

    def forward(self, X, infer=False):
        if infer:
            output = torch.mm(X, self.W_mu) + self.b_mu.expand(X.size()[0], self.n_output)
            return output

        epsilon_W, epsilon_b = self.get_random()
        W = self.W_mu + torch.log(1 + torch.exp(self.W_logsigma)) * epsilon_W
        b = self.b_mu + torch.log(1 + torch.exp(self.b_logsigma)) * epsilon_b
        output = torch.mm(X, W) + b.expand(X.size()[0], self.n_output)
        self.lpw = log_gaussian(W, 0, self.sigma_prior).sum() + log_gaussian(b, 0, self.sigma_prior).sum()
        self.lqw = log_gaussian_logsigma(W, self.W_mu, self.W_logsigma).sum() + log_gaussian_logsigma(b, self.b_mu, self.b_logsigma).sum()
        return output

    def get_random(self):
        return Variable(torch.Tensor(self.n_input, self.n_output).normal_(0, self.sigma_prior).cuda()), Variable(torch.Tensor(self.n_output).normal_(0, self.sigma_prior).cuda())


class MLP(nn.Module):
    def __init__(self, n_input, sigma_prior):
        super(MLP, self).__init__()
        self.l1 = MLPLayer(n_input, 200, sigma_prior)
        self.l1_relu = nn.ReLU()
        self.l2 = MLPLayer(200, 200, sigma_prior)
        self.l2_relu = nn.ReLU()
        self.l3 = MLPLayer(200, 10, sigma_prior)
        self.l3_softmax = nn.Softmax()

    def forward(self, X, infer=False):
        output = self.l1_relu(self.l1(X, infer))
        output = self.l2_relu(self.l2(output, infer))
        output = self.l3_softmax(self.l3(output, infer))
        return output

    def get_lpw_lqw(self):
        lpw = self.l1.lpw + self.l2.lpw + self.l3.lpw
        lqw = self.l1.lqw + self.l2.lqw + self.l3.lqw
        return lpw, lqw


def forward_pass_samples(X, y):
    s_log_pw, s_log_qw, s_log_likelihood = 0., 0., 0.
    for _ in xrange(n_samples):
        output = net(X)
        sample_log_pw, sample_log_qw = net.get_lpw_lqw()
        sample_log_likelihood = log_gaussian(y, output, sigma_prior).sum()
        s_log_pw += sample_log_pw
        s_log_qw += sample_log_qw
        s_log_likelihood += sample_log_likelihood

    return s_log_pw/n_samples, s_log_qw/n_samples, s_log_likelihood/n_samples


def criterion(l_pw, l_qw, l_likelihood):
    return ((1./n_batches) * (l_qw - l_pw) - l_likelihood).sum() / float(batch_size)

mnist = fetch_mldata('MNIST original')
N = 5000

data = np.float32(mnist.data[:]) / 255.
idx = np.random.choice(data.shape[0], N)
data = data[idx]
target = np.int32(mnist.target[idx]).reshape(N, 1)

train_idx, test_idx = train_test_split(np.array(range(N)), test_size=0.05)
train_data, test_data = data[train_idx], data[test_idx]
train_target, test_target = target[train_idx], target[test_idx]

train_target = np.float32(preprocessing.OneHotEncoder(sparse=False).fit_transform(train_target))

n_input = train_data.shape[1]
M = train_data.shape[0]
sigma_prior = float(np.exp(-3))
n_samples = 3
learning_rate = 0.001
n_epochs = 100

# Initialize network
net = MLP(n_input, sigma_prior)
net = net.cuda()

# building the objective
# remember, we're evaluating by samples
log_pw, log_qw, log_likelihood = 0., 0., 0.
batch_size = 100
n_batches = M / float(batch_size)
optimizer = torch.optim.Adam(net.parameters(), lr=learning_rate)

n_train_batches = int(train_data.shape[0] / float(batch_size))

for e in xrange(n_epochs):
    errs = []
    for b in range(n_train_batches):
        net.zero_grad()
        X = Variable(torch.Tensor(train_data[b * batch_size: (b+1) * batch_size]).cuda())
        y = Variable(torch.Tensor(train_target[b * batch_size: (b+1) * batch_size]).cuda())

        log_pw, log_qw, log_likelihood = forward_pass_samples(X, y)
        loss = criterion(log_pw, log_qw, log_likelihood)
        errs.append(loss.data.cpu().numpy())
        loss.backward()
        optimizer.step()

    X = Variable(torch.Tensor(test_data).cuda(), volatile=True)
    pred = net(X, infer=True)
    _, out = torch.max(pred, 1)
    acc = np.count_nonzero(np.squeeze(out.data.cpu().numpy()) == np.int32(test_target.ravel())) / float(test_data.shape[0])

    print 'epoch', e, 'loss', np.mean(errs), 'acc', acc