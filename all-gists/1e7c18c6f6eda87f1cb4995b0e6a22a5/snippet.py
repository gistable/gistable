import argparse
from collections import Counter
import csv
import os
import torch
from torch.autograd import Variable
import torch.nn as nn
import torch.optim as optim
import torch.utils.data as data
import tarfile
import time
import urllib.request

'''
This trains a classifier using Embedding -> tanh -> Linear -> CrossEntropyLoss
The goal is really just to get a sense of the speed of the Embedding layer in various cases,
there's not even any evaluation of the model :) (would be easy to add though)

$ python demo.py
$ python demo.py --sparse
$ python demo.py --cuda
$ python demo.py --cuda --sparse
'''

parser = argparse.ArgumentParser()
parser.add_argument('--cuda', action='store_true', help='use CUDA')
parser.add_argument('--sparse', action='store_true', help='use sparse updates for embedding layer')
parser.add_argument('--nepochs', type=int, default=10, help='number of epochs')
parser.add_argument('--ntoken', type=int, default=1000000, help='maximum dictionary size')
parser.add_argument('--nhid', type=int, default=100, help='hidden layer size')
parser.add_argument('--batch-size', type=int, default=100, help='batch size')
opt = parser.parse_args()

nclasses = 14
url = 'https://github.com/le-scientifique/torchDatasets/raw/master/dbpedia_csv.tar.gz'
base_folder = '/tmp'
archive_folder = os.path.join(base_folder, 'dbpedia_csv')
train_file = os.path.join(archive_folder, 'train.csv')
test_file = os.path.join(archive_folder, 'test.csv')
Tensor = torch.cuda.FloatTensor if opt.cuda else torch.Tensor


class Dataset(data.Dataset):

    def __init__(self, dictionary, filepath):
        lengths = []
        indices = []
        targets = []

        with open(filepath, 'r') as fin:
            for row in csv.reader(fin):
                tokens = [i for i in [dictionary.get(x) for x in (row[1] + row[2]).split()] if i is not None]
                length = len(tokens)
                targets.append(int(row[0]) - 1)
                lengths.append(len(tokens))
                indices.extend(tokens)

        self.targets = torch.LongTensor(targets)
        self.lengths = torch.LongTensor(lengths)
        self.starts = self.lengths.cumsum(0) - self.lengths
        self.indices = torch.LongTensor(indices)

    def __getitem__(self, index):
        start = self.starts[index]
        length = self.lengths[index]
        indices = self.indices[start:start + length] if length > 0 else None
        return length, indices, self.targets[index]

    def __len__(self):
        return self.lengths.numel()


class Model(nn.Module):

    def __init__(self, ntoken, nhid, nclasses):
        super(Model, self).__init__()
        self.embedding = nn.Embedding(opt.ntoken, opt.nhid, sparse=opt.sparse)
        self.linear = nn.Linear(opt.nhid, nclasses)

    def forward(self, lengths, indices):
        embeddings = Variable(Tensor(lengths.numel(), opt.nhid))
        starts = lengths.data.cumsum(0) - lengths.data
        for i, length in enumerate(lengths.data):
            if length > 0:
                start = starts[i]
                embeddings[i] = self.embedding(indices[start:start + length]).sum(dim=0).squeeze(0) / length
            else:
                embeddings[i] = torch.zeros(opt.nhid)
        return self.linear(embeddings.tanh())


def collate(batch):
    lengths = torch.LongTensor([x[0] for x in batch])
    indices = torch.cat([x[1] for x in batch if x[1] is not None])
    targets = torch.LongTensor([x[2] for x in batch])
    return lengths, indices, targets


def load_dictionary(filepath):
    cnt = Counter()
    with open(filepath, 'r') as fin:
        for row in csv.reader(fin):
            for token in (row[1] + row[2]).split():
                cnt[token] += 1
    return {e: i for i, (e, _) in enumerate(cnt.most_common(opt.ntoken))}


print('Downloading dataset')
if not os.path.exists(archive_folder):
    with urllib.request.urlopen(url, timeout=15) as stream, \
            tarfile.open(fileobj=stream, mode='r|gz') as tf:
        tf.extractall(base_folder)

print('Initializing model')
model = Model(opt.ntoken, opt.nhid, nclasses)
if opt.cuda:
    model.cuda()

print('Building dictionary')
dictionary = load_dictionary(train_file)

print('Loading dataset')
train_data = Dataset(dictionary, train_file)
train_dataloader = data.DataLoader(train_data, batch_size=opt.batch_size, shuffle=True, collate_fn=collate)
# test_data = Dataset(dictionary, test_file)
# test_dataloader = data.DataLoader(test_data, batch_size=opt.batch_size, collate_fn=collate)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adagrad(model.parameters(), lr=0.1)
start_time = time.time()
total_batches = 0

print('Training')
for i in range(opt.nepochs):
    for j, inputs in enumerate(train_dataloader):
        optimizer.zero_grad()
        lengths, indices, targets = [Variable(x.cuda() if opt.cuda else x) for x in inputs]
        probs = model(lengths, indices)
        loss = criterion(probs, targets)
        loss.backward()
        optimizer.step()
        total_batches += 1
        print('epoch: {}, batches: {}/{}, loss: {}, time/batch: {}'.format(
            i + 1, j + 1, len(train_dataloader), loss.data[0], (time.time() - start_time) / total_batches))
