# Collection of LSTM cells (including forget gates)
# https://en.wikipedia.org/w/index.php?title=Long_short-term_memory&oldid=784163987

import torch
from torch import nn
from torch.nn import Parameter
from torch.nn import functional as F
from torch.nn.modules.utils import _pair
from torch.autograd import Variable


class LSTMCell(nn.LSTMCell):
  def forward(self, input, hx):
    h, c = hx

    wx = F.linear(input, self.weight_ih, self.bias_ih)  # Weights combined into one matrix
    wh = F.linear(h, self.weight_hh, self.bias_hh)
    wxh = wx + wh

    i = F.sigmoid(wxh[:, :self.hidden_size])  # Input gate
    f = F.sigmoid(wxh[:, self.hidden_size:2 * self.hidden_size])  # Forget gate
    g = F.tanh(wxh[:, 2 * self.hidden_size:3 * self.hidden_size])  # Cell gate?
    o = F.sigmoid(wxh[:, 3 * self.hidden_size:])  # Output gate
    
    c = f * c + i * g  # Cell
    h = o * F.tanh(c)  # Hidden state
    return h, (h, c)


class PeepholeLSTMCell(nn.LSTMCell):
  def __init__(self, input_size, hidden_size, bias=True):
    super(PeepholeLSTMCell, self).__init__(input_size, hidden_size, bias)
    self.weight_ch = Parameter(torch.Tensor(3 * hidden_size, hidden_size))
    if bias:
      self.bias_ch = Parameter(torch.Tensor(3 * hidden_size))
    else:
      self.register_parameter('bias_ch', None)
    self.register_buffer('wc_blank', torch.zeros(hidden_size))
    self.reset_parameters()

  def forward(self, input, hx):
    h, c = hx

    wx = F.linear(input, self.weight_ih, self.bias_ih)
    wh = F.linear(h, self.weight_hh, self.bias_hh)
    wc = F.linear(c, self.weight_ch, self.bias_ch)
    wxhc = wx + wh + torch.cat((wc[:, :2 * self.hidden_size], Variable(self.wc_blank).expand_as(h), wc[:, 2 * self.hidden_size:]), 1)

    i = F.sigmoid(wxhc[:, :self.hidden_size])
    f = F.sigmoid(wxhc[:, self.hidden_size:2 * self.hidden_size])
    g = F.tanh(wxhc[:, 2 * self.hidden_size:3 * self.hidden_size])  # No cell involvement
    o = F.sigmoid(wxhc[:, 3 * self.hidden_size:])
    
    c = f * c + i * g
    h = o * F.tanh(c)
    return h, (h, c)


class Conv2dLSTMCell(nn.Module):
  def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding=0, dilation=1, groups=1, bias=True):
    super(Conv2dLSTMCell, self).__init__()
    if in_channels % groups != 0:
        raise ValueError('in_channels must be divisible by groups')
    if out_channels % groups != 0:
        raise ValueError('out_channels must be divisible by groups')
    kernel_size = _pair(kernel_size)
    stride = _pair(stride)
    padding = _pair(padding)
    dilation = _pair(dilation)
    self.in_channels = in_channels
    self.out_channels = out_channels
    self.kernel_size = kernel_size
    self.stride = stride
    self.padding = padding
    self.padding_h = tuple(k // 2 for k, s, p, d in zip(kernel_size, stride, padding, dilation))
    self.dilation = dilation
    self.groups = groups
    self.weight_ih = Parameter(torch.Tensor(4 * out_channels, in_channels // groups, *kernel_size))
    self.weight_hh = Parameter(torch.Tensor(4 * out_channels, out_channels // groups, *kernel_size))
    self.weight_ch = Parameter(torch.Tensor(3 * out_channels, out_channels // groups, *kernel_size))
    if bias:
      self.bias_ih = Parameter(torch.Tensor(4 * out_channels))
      self.bias_hh = Parameter(torch.Tensor(4 * out_channels))
      self.bias_ch = Parameter(torch.Tensor(3 * out_channels))
    else:
      self.register_parameter('bias_ih', None)
      self.register_parameter('bias_hh', None)
      self.register_parameter('bias_ch', None)
    self.register_buffer('wc_blank', torch.zeros(out_channels))
    self.reset_parameters()

  def reset_parameters(self):
    n = 4 * self.in_channels
    for k in self.kernel_size:
      n *= k
    stdv = 1. / math.sqrt(n)
    self.weight_ih.data.uniform_(-stdv, stdv)
    self.weight_hh.data.uniform_(-stdv, stdv)
    self.weight_ch.data.uniform_(-stdv, stdv)
    if self.bias_ih is not None:
      self.bias_ih.data.uniform_(-stdv, stdv)
      self.bias_hh.data.uniform_(-stdv, stdv)
      self.bias_ch.data.uniform_(-stdv, stdv)

  def forward(self, input, hx):
    h_0, c_0 = hx

    wx = F.conv2d(input, self.weight_ih, self.bias_ih, self.stride, self.padding, self.dilation, self.groups)
    wh = F.conv2d(h_0, self.weight_hh, self.bias_hh, self.stride, self.padding_h, self.dilation, self.groups)
    # Cell uses a Hadamard product instead of a convolution?
    wc = F.conv2d(c_0, self.weight_ch, self.bias_ch, self.stride, self.padding_h, self.dilation, self.groups)
    wxhc = wx + wh + torch.cat((wc[:, :2 * self.out_channels], Variable(self.wc_blank).expand(wc.size(0), wc.size(1) // 3, wc.size(2), wc.size(3)), wc[:, 2 * self.out_channels:]), 1)

    i = F.sigmoid(wxhc[:, :self.out_channels])
    f = F.sigmoid(wxhc[:, self.out_channels:2 * self.out_channels])
    g = F.tanh(wxhc[:, 2 * self.out_channels:3 * self.out_channels])
    o = F.sigmoid(wxhc[:, 3 * self.out_channels:])
    
    c_1 = f * c_0 + i * g
    h_1 = o * F.tanh(c_1)
    return h_1, (h_1, c_1)


lstm = LSTMCell(2, 1)
peeplstm = PeepholeLSTMCell(2, 1)
convlstm = Conv2dLSTMCell(2, 1, (3, 5), stride=1, padding=(0, 1))

x = Variable(torch.ones(1, 2))
h = Variable(torch.ones(1, 1))
c = Variable(torch.ones(1, 1))
t = Variable(torch.zeros(1, 1))

y, hx = lstm(x, (h, c))
loss = (y - t).mean()
loss.backward()

y, hx = peeplstm(x, (h, c))
loss = (y - t).mean()
loss.backward()

x.data.resize_(1, 2, 22, 22).random_()
h.data.resize_(1, 1, 20, 20).random_()
c.data.resize_(1, 1, 20, 20).random_()
t.data.resize_(1, 1, 20, 20).random_()

y, hx = convlstm(x, (h, c))
loss = (y - t).mean()
loss.backward()