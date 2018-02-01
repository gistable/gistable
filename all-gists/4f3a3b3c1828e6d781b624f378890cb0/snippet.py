# An implementation of "Machine Learning on Sequential Data Using a Recurrent Weighted Average" using pytorch 
# https://arxiv.org/pdf/1703.01253.pdf
#
# 
# This is a RNN (recurrent neural network) type that uses a weighted average of values seen in the past, rather
# than a separate running state.
# 
# Check the test code at the bottom for an example of usage, where you can compare it's performance
# against LSTM and GRU, at a classification task from the paper. It handily beats both the LSTM and 
# GRU :)
#
# Enjoy, and if you find it useful, drop me a line at richardweiss@richardweiss.org

import torch
from torch.autograd import Variable
import numpy as np


class RWA(torch.nn.Module):
    def __init__(self, input_shape, inner_shape):
        super().__init__()
        self.input_shape = input_shape
        self.inner_shape = inner_shape
        self.initial_state = torch.nn.Parameter(torch.randn(inner_shape))
        self.u_transform = torch.nn.Linear(input_shape, inner_shape)
        self.g_transform = torch.nn.Linear(input_shape+inner_shape, inner_shape)
        self.a_transform = torch.nn.Linear(input_shape+inner_shape, inner_shape, bias=False)

    def forward(self, x):
        # (seq_len, batch, input_size)
        batch_size = x.size()[1]
        activation = torch.nn.Tanh()
        hts = []

        n = Variable(torch.zeros([batch_size, self.inner_shape]), requires_grad=True)
        d = Variable(torch.zeros([batch_size, self.inner_shape]), requires_grad=True)
        ht = activation(self.initial_state.expand(batch_size, self.inner_shape))
        for step in range(x.size()[0]):
            x_step = x[step, :, :]
            x_merge = torch.cat([x_step, ht], 1)

            u = self.u_transform(x_step)
            g = self.g_transform(x_merge)
            a = self.a_transform(x_merge)

            z = u * activation(g)

            n = n + z * torch.exp(a)
            d = d + torch.exp(a)

            ht = activation(n / d)
            hts.append(ht)
        return torch.stack(hts, 0), ht

def npvariable(nparr, requires_grad=False):
    return Variable(torch.from_numpy(nparr), requires_grad=requires_grad)

if __name__ == '__main__':
    def make_seqlen_task():
        seq_lens = np.random.choice(500, size=64)
        seqs = np.zeros([500, 64, 1], dtype=np.float32)
        for i in range(64):
            seqs[:seq_lens[i], i, :] = np.random.uniform()
        y = seq_lens > 250

        return npvariable(seqs, True), npvariable(y.astype(np.float32))

    make_seqlen_task()

    num_cells = 128
    c = 'rwa'
    if c == 'lstm':
        rwa = torch.nn.LSTM(1, num_cells, 1)
    elif c == 'gru':
        rwa = torch.nn.GRU(1, num_cells, 1)
    else:
        rwa = RWA(1, num_cells)
    output_transform = torch.nn.Linear(num_cells, 1)

    opt = torch.optim.Adam(list(rwa.parameters()) + list(output_transform.parameters()))
    for i in range(100):
        opt.zero_grad()
        x, y = make_seqlen_task()
        _, v = rwa.forward(x)

        if c == 'lstm':
            preds = torch.nn.Sigmoid()(output_transform(v[0][0]))
        elif c == 'gru':
            preds = torch.nn.Sigmoid()(output_transform(v[0]))
        else:
            preds = torch.nn.Sigmoid()(output_transform(v))
        loss = torch.nn.MSELoss()(preds, y)
        loss.backward()
        if i % 10 == 0:
            print('%d: %f' % (i, loss.data.numpy()[0]))
        opt.step()

    losses = []
    for i in range(50):
        x, y = make_seqlen_task()
        _, v = rwa.forward(x)

        if c == 'lstm':
            preds = torch.nn.Sigmoid()(output_transform(v[0][0]))
        elif c == 'gru':
            preds = torch.nn.Sigmoid()(output_transform(v[0]))
        else:
            preds = torch.nn.Sigmoid()(output_transform(v))
        loss = torch.nn.MSELoss()(preds, y)
        losses.append(loss.data.numpy()[0])
    print(c, np.mean(losses))