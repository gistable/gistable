"""
DyNet implementation of a sequence labeler (POS taggger).
This is a translation of this tagger in PyTorch: https://gist.github.com/hal3/8c170c4400576eb8d0a8bd94ab231232

Basic architecture:
 - take words
 - run though bidirectional GRU
 - predict labels one word at a time (left to right), using a recurrent neural network "decoder"
The decoder updates hidden state based on:
 - most recent word
 - the previous action (aka predicted label).
 - the previous hidden state
 
Wall-clock time for PyTorch: 14.309s
Wall-clock time for DyNet:   1.749s
"""

from __future__ import division
import random
import pickle
import dynet as dy
import numpy as np

def reseed(seed=90210):
    random.seed(seed)
    # torch.manual_seed(seed)

reseed()

class Example(object):
    def __init__(self, tokens, labels, n_labels):
        self.tokens = tokens
        self.labels = labels
        self.n_labels = n_labels

def minibatch(data, minibatch_size, reshuffle):
    if reshuffle:
        random.shuffle(data)
    for n in xrange(0, len(data), minibatch_size):
        yield data[n:n+minibatch_size]

def bi_gru(f_gru, b_gru, embed):
    f_emb = f_gru.initial_state().transduce(embed)
    b_emb = reversed(b_gru.initial_state().transduce(reversed(embed)))
    return [dy.concatenate([f,b]) for f,b in zip(f_emb,b_emb)]

def test_wsj():
    print
    print '# test on wsj subset'

    data, n_types, n_labels = pickle.load(open('wsj.pkl', 'r'))

    d_emb = 50
    d_rnn = 51
    d_hid = 52
    d_actemb = 5

    minibatch_size = 5
    n_epochs = 10
    preprocess_minibatch = True
    
    model = dy.ParameterCollection()

    embed_word = model.add_lookup_parameters((n_types, d_emb))
    f_gru = dy.GRUBuilder(1, d_emb, d_rnn, model)
    b_gru = dy.GRUBuilder(1, d_emb, d_rnn, model)
    embed_action = model.add_lookup_parameters((n_labels, d_actemb))
    combine_arh_W = model.add_parameters((d_hid, d_actemb + d_rnn * 2 + d_hid))
    combine_arh_b = model.add_parameters(d_hid)
    
    initial_h = model.add_parameters(d_hid, dy.ConstInitializer(0))
    initial_actemb = model.add_parameters(d_actemb, dy.ConstInitializer(0))

    policy_W = model.add_parameters((n_labels, d_hid))
    policy_b = model.add_parameters(n_labels)

    optimizer = dy.AdamTrainer(model, alpha=0.01)
    
    for _ in xrange(n_epochs):

        total_loss = 0
        for batch in minibatch(data, minibatch_size, True):
            dy.renew_cg()

            combine_arh_We = dy.parameter(combine_arh_W)
            combine_arh_be = dy.parameter(combine_arh_b)

            policy_We = dy.parameter(policy_W)
            policy_be = dy.parameter(policy_b)

            loss = 0

            if preprocess_minibatch:
                # for efficiency, combine RNN outputs on entire
                # minibatch in one go (requires padding with zeros,
                # should be masked but isn't right now)
                all_tokens = [ex.tokens for ex in batch]
                max_length = max(map(len, all_tokens))
                all_tokens = [[x[i] if len(x) > i else 0 for x in all_tokens] for i in range(max_length)]
                all_e = [dy.lookup_batch(embed_word, x) for x in all_tokens]
                all_rnn_out = bi_gru(f_gru, b_gru, all_e)
            
            losses = []
            for batch_id, ex in enumerate(batch):
                N = len(ex.tokens)
                if preprocess_minibatch:
                    rnn_out = [dy.pick_batch_elem(x, batch_id) for x in all_rnn_out[:N]]
                else:
                    e = [embed_word[x] for x in ex.tokens]
                    rnn_out = bi_gru(f_gru, b_gru, e)
                prev_h = dy.parameter(initial_h)  # previous hidden state
                actemb = dy.parameter(initial_actemb)  # embedding of previous action
                output = []
                for t in xrange(N):
                    # update hidden state based on most recent
                    # *predicted* action (not ground truth)
                    inputs = [actemb, prev_h, rnn_out[t]]
                    h = dy.rectify(dy.affine_transform([combine_arh_be, combine_arh_We, dy.concatenate(inputs)]))

                    # make prediction
                    pred_vec = dy.affine_transform([policy_be, policy_We, h])
                    pred = pred_vec.npvalue().argmin()
                    output.append(pred)

                    # accumulate loss (squared error against costs)
                    truth = np.ones(n_labels)
                    truth[ex.labels[t]] = 0
                    losses.append(dy.squared_distance(pred_vec, dy.inputTensor(truth)))

                    # cache hidden state, previous action embedding
                    prev_h = h
                    actemb = embed_action[pred]

                # print 'output=%s, truth=%s' % (output, ex.labels)

            loss = dy.esum(losses)
            loss.backward()
            total_loss += loss.value()
            optimizer.update()
        print total_loss

    
if __name__ == '__main__':
    test_wsj()