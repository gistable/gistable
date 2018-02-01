#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Paragraph Vector on Chainer
"""
import argparse
import collections
import time

import numpy as np
import six.moves.cPickle as pickle

import chainer
from chainer import cuda
import chainer.functions as F
import chainer.optimizers as O

parser = argparse.ArgumentParser()
parser.add_argument('--gpu', '-g', default=-1, type=int,
                    help='GPU ID (negative value indicates CPU)')
parser.add_argument('--unit', '-u', default=100, type=int,
                    help='number of units')
parser.add_argument('--window', '-w', default=5, type=int,
                    help='window size')
parser.add_argument('--batchsize', '-b', type=int, default=32,
                    help='learning minibatch size')
parser.add_argument('--epoch', '-e', default=10, type=int,
                    help='number of epochs to learn')
parser.add_argument('--model', '-m', choices=['skipgram'],
                    default='skipgram',
                    help='model type ("skipgram")')
parser.add_argument('--out-type', '-o', choices=['hsm', 'ns', 'original'],
                    default='ns',
                    help='output model type ("hsm": hierarchical softmax, '
                    '"ns": negative sampling, "original": no approximation)')
args = parser.parse_args()
if args.gpu >= 0:
    cuda.check_cuda_available()
xp = cuda.cupy if args.gpu >= 0 else np

print('GPU: {}'.format(args.gpu))
print('# unit: {}'.format(args.unit))
print('Window: {}'.format(args.window))
print('Minibatch-size: {}'.format(args.batchsize))
print('# epoch: {}'.format(args.epoch))
print('Training model: {}'.format(args.model))
print('Output type: {}'.format(args.out_type))
print('')


# def continuous_bow(dataset, position):
#     h = None

#     # use random window size in the same way as the original word2vec
#     # implementation.
#     w = np.random.randint(args.window - 1) + 1
#     for offset in range(-w, w + 1):
#         if offset == 0:
#             continue
#         d = xp.asarray(dataset[position + offset])
#         x = chainer.Variable(d)
#         e = model.embed(x)
#         h = h + e if h is not None else e

#     d = xp.asarray(dataset[position])
#     t = chainer.Variable(d)
#     return loss_func(h, t)


def skip_gram_pv(minibatch_doc, doc_ids, max_len, position):
    doc_ids = chainer.Variable(doc_ids, volatile=True)
    doc_embs = model.pvembed(doc_ids)
    # use random window size in the same way as the original word2vec
    # implementation.
    # w = np.random.randint(args.window - 1) + 1
    loss = None
    for i in xrange(max_len):
        # for offset in range(max(i-w, 0), min(i+w+1,max_len)):
        # if offset == i:
            # continue
        # print type(minibatch_doc)
        # print type(position + offset)
        # minibatch_doc = xp.ndarray(minibatch_doc)
        # d = xp.asarray(minibatch_doc[position + offset], dtype=xp.int32)
        d = xp.asarray(minibatch_doc[position + i], dtype=xp.int32)
        # print "position:",position
        # print "offset:",position + offset
        # print "d:"
        # print d
        # d = xp.asarray(dataset[position + offset])
        x = chainer.Variable(d, volatile=True)
        # e = model.embed(x)
        # print e.data
        # print t.data

        loss_i = loss_func(doc_embs, x)
        loss = loss_i if loss is None else loss + loss_i
    return loss


if args.gpu >= 0:
    cuda.get_device(args.gpu).use()

index2word = {}
word2index = {}
counts = collections.Counter()
dataset = []
dataset_doc = []
word2index['*NULL*'] = 0 # NULL文字
with open('ptb.train.txt') as f:
    for line in f:
        word_idxs = []
        for word in line.split():
            if word not in word2index:
                ind = len(word2index)
                word2index[word] = ind
                index2word[ind] = word
            counts[word2index[word]] += 1
            dataset.append(word2index[word])
            word_idxs.append(word2index[word])
        dataset_doc.append(word_idxs)

n_doc = len(dataset_doc)
n_vocab = len(word2index)

print('n_doc: %d' % n_doc)
print('n_vocab: %d' % n_vocab)
print('data length: %d' % len(dataset))

if args.model == 'skipgram':
    train_model = skip_gram_pv
# elif args.model == 'cbow':
#     train_model = continuous_bow
else:
    raise Exception('Unknown model type: {}'.format(args.model))

model = chainer.FunctionSet(
    # embed=F.EmbedID(n_vocab, args.unit),
    pvembed=F.EmbedID(n_doc, args.unit),
)

if args.out_type == 'hsm':
    HSM = F.BinaryHierarchicalSoftmax
    tree = HSM.create_huffman_tree(counts)
    model.l = HSM(args.unit, tree)
    loss_func = model.l
elif args.out_type == 'ns':
    cs = [counts[w] for w in range(len(counts))]
    model.l = F.NegativeSampling(args.unit, cs, 20)
    loss_func = model.l
elif args.out_type == 'original':
    model.l = F.Linear(args.unit, n_vocab)
    loss_func = lambda h, t: F.softmax_cross_entropy(model.l(h), t)
else:
    raise Exception('Unknown output type: {}'.format(args.out_type))

if args.gpu >= 0:
    model.to_gpu()

dataset = np.array(dataset, dtype=np.int32)

optimizer = O.Adam()
optimizer.setup(model)

begin_time = time.time()
cur_at = begin_time
word_count = 0
skip = (len(dataset) - args.window * 2) // args.batchsize
skip_doc = len(dataset_doc) // args.batchsize + 1
skip_doc_end = len(dataset_doc) - skip_doc*args.batchsize
print "dataset : ", len(dataset)
print "skip :", skip
print "skip_doc:", skip_doc
print "skip_doc_end :", skip_doc_end
next_count = 10000

null_index = word2index['*NULL*']

for epoch in range(args.epoch):
    accum_loss = 0
    print('#epoch: {0}'.format(epoch))

    # n_doc loop
    # np.array(range(0, args.batchsize)) * skip_doc + (args.window + i)
    # for doc_id in range(n_doc):

    for i in xrange(skip_doc):

        if word_count >= next_count:
            now = time.time()
            duration = now - cur_at
            print('{} words, {:.2f} sec'.format(next_count, duration))
            cur_at = now
            next_count += 10000

        end_doc_idx = args.batchsize
        doc_batch_idx = np.array(range(i*args.batchsize, (i+1)*args.batchsize))
        postion_length = args.batchsize
        if i == skip_doc-1:
            # print "*"
            doc_batch_idx = doc_batch_idx[:skip_doc_end]
            postion_length = args.batchsize + skip_doc_end

        max_len = max([len(dataset_doc[doc_id]) for doc_id in doc_batch_idx])
        position = np.array([_i*max_len for _i in range(0, postion_length)], dtype=np.int32)
        # print doc_batch_idx
        # print '**'
        # print "max_len :", max_len

        minibatch_doc = []
        for doc_id in doc_batch_idx:
            doc = dataset_doc[doc_id]
            for _i in xrange(len(doc),max_len):
                doc.append(null_index)
            minibatch_doc += doc

        # minibatch_doc = xp.asarray(minibatch_doc)
        minibatch_doc = np.array(minibatch_doc, dtype=np.int32)
        # print minibatch_doc.shape
        doc_batch_idx = np.array(doc_batch_idx, dtype=np.int32)
        loss = train_model(minibatch_doc, doc_batch_idx, max_len, position)
        accum_loss += loss.data
        word_count += args.batchsize
        optimizer.zero_grads()
        loss.backward()
        optimizer.update()



    # indexes = np.random.permutation(skip)
    # for i in indexes:
    #     if word_count >= next_count:
    #         now = time.time()
    #         duration = now - cur_at
    #         throuput = 100000. / (now - cur_at)
    #         print('{} words, {:.2f} sec, {:.2f} words/sec'.format(
    #             word_count, duration, throuput))
    #         next_count += 100000
    #         cur_at = now

    #     position = np.array(
    #         range(0, args.batchsize)) * skip + (args.window + i)
    #     loss = train_model(dataset, position)
    #     accum_loss += loss.data
    #     word_count += args.batchsize

    #     optimizer.zero_grads()
    #     loss.backward()
    #     optimizer.update()

    print(accum_loss)

model.to_cpu()
with open('model.pickle', 'wb') as f:
    obj = (model, model.l.W ,index2word, word2index)
    pickle.dump(obj, f)
