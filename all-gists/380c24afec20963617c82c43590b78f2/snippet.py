'''
Original implementation
https://github.com/clab/dynet_tutorial_examples/blob/master/tutorial_parser.ipynb

The code structure and variable names are similar for better reference.

Not for serious business, just for some comparison between PyTorch and DyNet
(and I still prefer PyTorch)
'''
import torch as T
import torch.nn as NN
import torch.nn.functional as F
from torch.autograd import Variable
import argparse

import numpy as NP
import numpy.random as RNG
import re

# Argument parsing

parser = argparse.ArgumentParser()
parser.add_argument("--worddim",
                    help="dimension of word embedding",
                    type=int,
                    default=64)
parser.add_argument("--lstmdim",
                    help="dimension of LSTM hidden state",
                    type=int,
                    default=64)
parser.add_argument("--actiondim",
                    help="dimension of action layer",
                    type=int,
                    default=32)
parser.add_argument("--cuda",
                    help="use cuda",
                    action="store_true")

args = parser.parse_args()

WORD_DIM = args.worddim
LSTM_DIM = args.lstmdim
ACTION_DIM = args.actiondim

# Helper functions

def variable(*args_, **kwargs):
    v = Variable(*args_, **kwargs)
    return v.cuda() if args.cuda else v

def var_to_numpy(v):
    return (v.cpu() if args.cuda else v).data.numpy()

def zerovar(*size):
    return variable(T.zeros(*size))

# Same thing as original implementation

class Vocab(object):
    def __init__(self, w2i):
        self.w2i = dict(w2i)
        self.i2w = {i:w for w, i in w2i.iteritems()}

    @classmethod
    def from_list(cls, words):
        return Vocab({w: i for i, w in enumerate(words)})

    @classmethod
    def from_file(cls, filename):
        words = []
        f = open(filename)
        for l in f:
            l = l.strip()
            w, c = l.split()
            words.append(w)
        f.close()
        return Vocab.from_list(words)

    def size(self):
        return len(self.w2i.keys())

def read_oracle(fname, vw, va):
    with open(fname) as f:
        for line in f:
            line = line.strip()
            ssent, sacts = re.split(r' \|\|\| ', line)
            sent = [vw.w2i[x] for x in ssent.split()]
            acts = [va.w2i[x] for x in sacts.split()]
            sent.reverse()
            acts.reverse()
            yield sent, acts

acts = ['SHIFT', 'REDUCE_L', 'REDUCE_R']
vocab_acts = Vocab.from_list(acts)
SHIFT = vocab_acts.w2i['SHIFT']
REDUCE_L = vocab_acts.w2i['REDUCE_L']
REDUCE_R = vocab_acts.w2i['REDUCE_R']
NUM_ACTIONS = vocab_acts.size()


class StackRNN(object):
    def __init__(self,
                 cell,
                 initial_state,
                 get_output,
                 p_empty_embedding=None):
        self.cell = cell
        self.s = [(initial_state, None)]
        self.empty = None
        self.get_output = get_output
        if p_empty_embedding:
            self.empty = p_empty_embedding

    def push(self, expr, extra=None):
        self.s.append((self.cell(expr, self.s[-1][0]), extra))

    def pop(self):
        return self.s.pop()[1]

    def embedding(self):
        return self.get_output(self.s[-1][0]) if len(self.s) > 1 else self.empty

    def __len__(self):
        return len(self.s) - 1


class TransitionParser(NN.Module):
    def __init__(self, vocab):
        super(TransitionParser, self).__init__()

        self.vocab = vocab

        self.p_comp = NN.Linear(LSTM_DIM * 2, LSTM_DIM)
        self.p_s2h = NN.Linear(LSTM_DIM * 2, LSTM_DIM)
        self.p_act = NN.Linear(LSTM_DIM, NUM_ACTIONS)

        self.buff_rnn_cell = NN.LSTMCell(WORD_DIM, LSTM_DIM)
        self.stack_rnn_cell = NN.LSTMCell(WORD_DIM, LSTM_DIM)
        self.pempty_buffer_emb = NN.Parameter(T.randn(1, LSTM_DIM))
        self.WORDS_LOOKUP = NN.Embedding(vocab.size(), WORD_DIM)

    def _rnn_get_output(self, state):
        return state[0]

    def forward(self, tokens, oracle_actions=None):
        tokens = variable(T.LongTensor(tokens))
        # I think DyNet implementation is doing single-sample SGD.
        def _valid_actions(stack, buffer_):
            valid_actions= []
            if len(buffer_) > 0:
                valid_actions += [SHIFT]
            if len(stack) >= 2:
                valid_actions += [REDUCE_L, REDUCE_R]
            return valid_actions

        if oracle_actions:
            oracle_actions = list(oracle_actions)

        # Since we are using LSTMCell here we should specify initial state
        # manually.
        buffer_initial = (zerovar(1, LSTM_DIM), zerovar(1, LSTM_DIM))
        stack_initial = (zerovar(1, LSTM_DIM), zerovar(1, LSTM_DIM))
        buffer_ = StackRNN(self.buff_rnn_cell, buffer_initial,
                           self._rnn_get_output, self.pempty_buffer_emb)
        stack = StackRNN(self.stack_rnn_cell, stack_initial,
                         self._rnn_get_output)

        losses = []

        tok_embeddings = self.WORDS_LOOKUP(tokens.unsqueeze(0))[0] # batch dim
        for i in range(tok_embeddings.size()[0]):
            tok_embedding = tok_embeddings[i].unsqueeze(0)
            tok = tokens[i].data.numpy()[0]
            buffer_.push(tok_embedding, (tok_embedding, self.vocab.i2w[tok]))

        while not (len(stack) == 1 and len(buffer_) == 0):
            valid_actions = _valid_actions(stack, buffer_)
            log_probs = None
            action = valid_actions[0]
            if len(valid_actions) > 1:
                p_t = T.cat([buffer_.embedding(), stack.embedding()], 1)
                h = T.tanh(self.p_s2h(p_t))
                logits = self.p_act(h)[0][T.LongTensor(valid_actions)]
                valid_action_tbl = {a: i for i, a in enumerate(valid_actions)}
                log_probs = F.log_softmax(logits)
                if oracle_actions is None:
                    action_idx = T.max(log_probs, 0)[1][0].data.numpy()[0]
                    action = valid_actions[action_idx]
            if oracle_actions is not None:
                action = oracle_actions.pop()
            if log_probs is not None:
                losses.append(log_probs[valid_action_tbl[action]])

            if action == SHIFT:
                tok_embedding, token = buffer_.pop()
                stack.push(tok_embedding, (tok_embedding, token))
            else:
                right = stack.pop()
                left = stack.pop()
                head, modifier = ((left, right) if action == REDUCE_R
                                  else (right, left))
                head_rep, head_tok = head
                mod_rep, mod_tok = modifier
                comp_rep = T.cat([head_rep, mod_rep], 1)
                comp_rep = T.tanh(self.p_comp(comp_rep))

                stack.push(comp_rep, (comp_rep, head_tok))
                if oracle_actions is None:
                    print '%s --> %s' % (head_tok, mod_tok)

        if oracle_actions is None:
            head = stack.pop()[1]
            print 'ROOT --> %s' % head
        return -T.sum(T.cat(losses)) if len(losses) > 0 else None


vocab_words = Vocab.from_file('data/vocab.txt')
train = list(read_oracle('data/small-train.unk.txt', vocab_words, vocab_acts))
dev = list(read_oracle('data/small-dev.unk.txt', vocab_words, vocab_acts))

model = TransitionParser(vocab_words)
if args.cuda:
    model.cuda()

opt = T.optim.SGD(model.parameters(), lr=1e-6)

instances_processed = 0
validation_losses = []
for epoch in range(5):
    RNG.shuffle(train)
    words = 0
    total_loss = 0.
    for (s, a) in train:
        e = instances_processed // len(train)
        if instances_processed % 1000 == 0:
            model.eval()
            dev_words = 0
            dev_loss = 0.
            for (ds, da) in dev:
                loss = model.forward(ds, da)
                dev_words += len(ds)
                if loss is not None:
                    dev_loss += loss.data.numpy()
            print ('[valid] epoch %d: per-word loss: %.6f' %
                   (e, dev_loss / dev_words))
            validation_losses.append(dev_loss)

        if instances_processed % 100 == 0 and words > 0:
            print 'epoch %d: per-word loss: %.6f' % (e, total_loss / words)
            words = 0
            total_loss = 0.

        model.train()
        loss = model.forward(s, a)
        words += len(s)
        instances_processed += 1

        if loss is not None:
            total_loss += loss.data.numpy()
            loss.backward()
            opt.step()

s = 'Parsing in Austin is fun .'
UNK = vocab_words.w2i['<unk>']
toks = [vocab_words.w2i[x] if x in vocab_words.w2i else UNK for x in s.split()]
toks.reverse()
model.forward(toks, None)
