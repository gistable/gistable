"""
TreeLSTM[1] implementation in Pytorch

Based on dynet benchmarks : 
  https://github.com/neulab/dynet-benchmark/blob/master/dynet-py/treenn.py
  https://github.com/neulab/dynet-benchmark/blob/master/chainer/treenn.py
Other References:
  https://github.com/pytorch/examples/tree/master/word_language_model
  https://github.com/pfnet/chainer/blob/29c67fe1f2140fa8637201505b4c5e8556fad809/chainer/functions/activation/slstm.py
  https://github.com/stanfordnlp/treelstm

[1] : Improved Semantic Representations From Tree-Structured Long Short-Term Memory Networks, https://arxiv.org/abs/1503.00075
"""
from __future__ import print_function
import time
start = time.time()

import re
import codecs
from collections import Counter
import random
import sys, os, progressbar
import argparse

import numpy as np
import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.optim as optim

widgets = [progressbar.Percentage(), ' ', progressbar.Bar(), ' ', progressbar.ETA()]
parser = argparse.ArgumentParser()
parser.add_argument('--data',dest='data',
                    help='path to data folder containing {train|dev|test}.txt, default=./data',default="./data")
parser.add_argument('--size-hidden',dest='n_hidden', type=int, help='hidden size')
parser.add_argument('--model',dest='model', help='model type rnn|lstm')
parser.add_argument('--timeout',dest='timeout',type=int, help='timeout in seconds')
parser.add_argument('--seed',dest='seed',type=int, help='seed',default=0)
parser.add_argument('--cuda', action='store_true',help='use CUDA')
args = parser.parse_args()

CUDA=args.cuda

torch.manual_seed(args.seed)
if torch.cuda.is_available():
  if not args.cuda:
    print("WARNING: You have a CUDA device, so you should probably run with --cuda")
  else:
    torch.cuda.manual_seed(args.seed)

def makevar(x):
  v = torch.from_numpy(np.array([x]))
  if CUDA:
    return Variable(v.cuda())
  return Variable(v)

def zeros(dim):
  v = torch.zeros(dim)
  if CUDA:
    return Variable(v.cuda())
  return Variable(v)

def _tokenize_sexpr(s):
  tokker = re.compile(r" +|[()]|[^ ()]+")
  toks = [t for t in [match.group(0) for match in tokker.finditer(s)] if t[0] != " "]
  return toks

def _within_bracket(toks):
  label = next(toks)
  children = []
  for tok in toks:
    if tok == "(":
      children.append(_within_bracket(toks))
    elif tok == ")":
      return Tree(label, children)
    else: children.append(Tree(tok, None))
  assert(False),list(toks)

class Tree(object):
  def __init__(self, label, children=None):
    self.label = label
    self.children = children

  @staticmethod
  def from_sexpr(string):
    toks = iter(_tokenize_sexpr(string))
    assert next(toks) == "("
    return _within_bracket(toks)

  def __str__(self):
    if self.children is None: return self.label
    return "[%s %s]" % (self.label, " ".join([str(c) for c in self.children]))

  def isleaf(self): return self.children==None

  def leaves_iter(self):
    if self.isleaf():
      yield self
    else:
      for c in self.children:
        for l in c.leaves_iter(): yield l

  def leaves(self): return list(self.leaves_iter())

  def nonterms_iter(self):
    if not self.isleaf():
      yield self
      for c in self.children:
        for n in c.nonterms_iter(): yield n

  def nonterms(self): return list(self.nonterms_iter())

def read_dataset(filename):
  return [Tree.from_sexpr(line.strip()) for line in codecs.open(filename,"r")]

def get_vocabs(trees):
  label_vocab = Counter()
  word_vocab  = Counter()
  for tree in trees:
    label_vocab.update([n.label for n in tree.nonterms()])
    word_vocab.update([l.label for l in tree.leaves()])
  labels = [x for x,c in label_vocab.iteritems() if c > 0]
  words   = ["_UNK_"] + [x for x,c in word_vocab.iteritems() if c > 0]
  l2i = {l:i for i,l in enumerate(labels)}
  w2i = {w:i for i,w in enumerate(words)}
  return l2i, w2i, labels, words

class TreeRNN(nn.Module):
  def __init__(self, word_vocab, hdim, nc):
    super(TreeRNN, self).__init__()
    self.embed = nn.Embedding(len(word_vocab), hdim)
    self.WR = nn.Linear(2*hdim, hdim)
    self.WO = nn.Linear(hdim, nc)
    self.WF = nn.Linear(hdim, hdim)
    self.TANH = nn.Tanh()
    self.RELU = nn.ReLU()
    self.SOFTMAX = nn.Softmax()
    self.w2i = word_vocab

  def expr_for_tree(self, tree, decorate=False):
    if tree.isleaf():
      return self.embed(makevar(self.w2i.get(tree.label, 0)))
    if len(tree.children) == 1:
      assert(tree.children[0].isleaf())
      expr = self.expr_for_tree(tree.children[0])
      if decorate:
        tree._e = expr
      return expr
    assert(len(tree.children) == 2), tree.children[0]
    e1 = self.expr_for_tree(tree.children[0], decorate)
    e2 = self.expr_for_tree(tree.children[1], decorate)
    expr = self.TANH(self.WR(torch.cat((e1, e2),1)))
    if decorate:
      tree._e = expr
    return expr

  def classify(self, e):
    return self.WO(self.RELU(self.WF(e)))


class TreeLSTM(nn.Module):
  def __init__(self, word_vocab, hdim, nc):
    super(TreeLSTM, self).__init__()
    self.embed = nn.Embedding(len(word_vocab), hdim)
    self.Wi = nn.Linear(hdim, hdim)
    self.Wo = nn.Linear(hdim, hdim)
    self.Wu = nn.Linear(hdim, hdim)

    self.Ui  = nn.Linear(2*hdim, hdim)
    self.Uo  = nn.Linear(2*hdim, hdim)
    self.Uu  = nn.Linear(2*hdim, hdim)

    self.Uf1 = nn.Linear(hdim, hdim)
    self.Uf2 = nn.Linear(hdim, hdim)

    self.WO = nn.Linear(hdim, nc)
    self.WF = nn.Linear(hdim, hdim)

    self.SIGM = nn.Sigmoid()
    self.TANH = nn.Tanh()
    self.RELU = nn.ReLU()
    self.SOFTMAX = nn.Softmax()
    self.w2i = word_vocab

  def expr_for_tree(self, tree, decorate=False):
    assert(not tree.isleaf())
    if len(tree.children) == 1:
      assert(tree.children[0].isleaf())
      emb = self.embed(makevar(self.w2i.get(tree.label, 0)))

      i = self.SIGM(self.Wi(emb))
      o = self.SIGM(self.Wo(emb))
      u = self.TANH(self.Wu(emb))
      c = i * u
      h = o * self.TANH(c)

      if decorate:
        tree._e = (h,c)
      return h, c

    assert(len(tree.children) == 2), tree.children[0]
    e1, c1 = self.expr_for_tree(tree.children[0], decorate)
    e2, c2 = self.expr_for_tree(tree.children[1], decorate)

    e  = torch.cat((e1, e2),1)
    i  = self.SIGM(self.Ui(e))
    o  = self.SIGM(self.Uo(e))
    f1 = self.SIGM(self.Uf1(e1))
    f2 = self.SIGM(self.Uf2(e2))
    u  = self.TANH(self.Uu(e))
    c  = i * u + f1*c1 + f2*c2
    h  = o * self.TANH(c)

    if decorate:
      tree._e = (h,c)
    return h,c

  def classify(self, e):
    return self.WO(self.RELU(self.WF(e[0])))


def evaluate(treenet, split):
  eval_start = time.time()
  n = correct = 0.0

  pbar = progressbar.ProgressBar(widgets = widgets, maxval=len(split)).start()
  for j,tree in enumerate(split):
    prediction = treenet.classify(treenet.expr_for_tree(tree, False)).data
    _,pred = torch.max(prediction,1)
    correct += (pred == l2i[tree.label]).sum()
    n += 1
    pbar.update(j)
  pbar.finish()
  eval_time = time.time() - eval_start
  return correct/n , len(split)/eval_time

trn = read_dataset(os.path.join(args.data,'train.txt'))
dev = read_dataset(os.path.join(args.data,'dev.txt'))
tst = read_dataset(os.path.join(args.data,'test.txt'))

l2i, w2i, i2l, i2w = get_vocabs(trn)

if args.model == 'rnn':
  treenet = TreeRNN(w2i, args.n_hidden, len(l2i))
elif args.model == 'lstm':
  treenet = TreeLSTM(w2i, args.n_hidden, len(l2i))
else:
  raise NotImplementedError()

if CUDA:
  treenet.cuda()

optimizer = optim.Adam(treenet.parameters())
optimizer.zero_grad()
criterion = nn.CrossEntropyLoss()


start_time = time.time()
print("startup time for %s model: %r" % (args.model,start_time - start))

for ITER in range(100):
  random.shuffle(trn)
  closs = 0.0
  cwords = 0
  trn_start = time.time()

  pbar = progressbar.ProgressBar(widgets = widgets, maxval=len(trn)).start()
  for i,tree in enumerate(trn,1):
    if args.model == 'rnn':
      h = treenet.expr_for_tree(tree,True)
    elif args.model == 'lstm':
      h,c = treenet.expr_for_tree(tree,True)
    else:
      raise NotImplementedError()

    nodes = tree.nonterms()
    losses = [criterion(treenet.classify(nt._e), makevar(l2i[nt.label])) for nt in nodes]
    loss = sum(losses)

    closs += float(loss.data[0])
    cwords += len(nodes)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    pbar.update(i)
  pbar.finish()

  trn_loss = closs / cwords
  trn_rate = len(trn)/(time.time() - trn_start)
  val_score, val_rate = evaluate(treenet, dev)

  print("\ntrn loss: {:5.3f} trn speed {:5.1f} sent/sec val acc: {:5.2f} val speed {:5.1f} sent/sec".format(trn_loss,trn_rate,val_score,val_rate))

  if time.time() - start_time > args.timeout:
    break

tst_score, tst_rate = evaluate(treenet,tst)
print("test acc: {:5.2f} test speed {:5.1f} sent/sec".format(tst_score,tst_rate))