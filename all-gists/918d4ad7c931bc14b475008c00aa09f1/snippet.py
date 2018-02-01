import torch
import torch.nn as nn
from torch.autograd import Variable
from torch.nn.utils.rnn import pad_packed_sequence, pack_padded_sequence

x = Variable(torch.randn(10, 20, 30)).cuda()
lens = range(10)

x = pack_padded_sequence(x, lens[::-1], batch_first=True)

lstm = nn.LSTM(30, 50, batch_first=True).cuda()
h0 = Variable(torch.zeros(1, 10, 50)).cuda()
c0 = Variable(torch.zeros(1, 10, 50)).cuda()

packed_h, (packed_h_t, packed_c_t) = lstm(x, (h0, c0))
h, _ = pad_packed_sequence(packed_h) 
print h.size() # Size 20 x 10 x 50 instead of 10 x 20 x 50