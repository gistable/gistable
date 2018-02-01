# Code for https://www.data-blogger.com/2017/12/14/create-a-character-based-seq2seq-using-python-and-tensorflow/

# Imports
import tensorflow as tf
import pandas as pd
from nltk import word_tokenize
from collections import Counter
import numpy as np

# Load the data
with open('hamlet.txt', 'r') as input_file:
    words_raw = input_file.read()
    
# Load the words
words = word_tokenize(words_raw)
words = [word.lower() for word in words]
chars = list(' '.join(words))
char_counts = Counter(chars)

# Add a PAD token (to fill up empty spaces), EOW token (for signaling the End-Of-Word) and UNK token (for unknown characters)
# Also use the 100 most frequent characters
vocab = ['PAD', 'EOW', 'UNK'] + [char for char, count in char_counts.most_common(100)]
vocab = {char: i for i, char in enumerate(vocab)}
vocab_size = len(vocab)

# Configuration
input_embedding_size = 20
encoder_hidden_units = 16

# Create the graph
tf.reset_default_graph()

# Create the encoder and decoder
encoder_inputs = tf.placeholder(shape=[None, None], dtype=tf.int32, name='encoder_inputs')
encoder_inputs_length = tf.placeholder(shape=[None,], dtype=tf.int32, name='encoder_input_length')
decoder_targets = tf.placeholder(shape=[None, None], dtype=tf.int32, name='decoder_targets')
embeddings = tf.Variable(tf.random_uniform([vocab_size, input_embedding_size], -1., 1.), dtype=tf.float32)
encoder_inputs_embedded = tf.nn.embedding_lookup(embeddings, encoder_inputs)
encoder_cell = tf.nn.rnn_cell.BasicLSTMCell(encoder_hidden_units)
((encoder_fw_outputs, encoder_bw_outputs), (encoder_fw_final_state, encoder_bw_final_state)) = tf.nn.bidirectional_dynamic_rnn(cell_fw=encoder_cell, cell_bw=encoder_cell, inputs=encoder_inputs_embedded, sequence_length=encoder_inputs_length, dtype=tf.float32, time_major=True)

# Okay, short notice: I use a stacked LSTM to encode both forward information (prefixes) and backward information (suffixes)
encoder_final_state_h = tf.concat([encoder_fw_final_state.h, encoder_fw_final_state.h], axis=1)
encoder_final_state_c = tf.concat([encoder_fw_final_state.c, encoder_bw_final_state.c], axis=1)
encoder_final_state = tf.contrib.rnn.LSTMStateTuple(
    c=encoder_final_state_c,
    h=encoder_final_state_h
)

# The decoder
decoder_hidden_units = 2 * encoder_hidden_units
decoder_cell = tf.nn.rnn_cell.BasicLSTMCell(decoder_hidden_units)
encoder_max_time, batch_size = tf.unstack(tf.shape(encoder_inputs))
# 3 is arbitrary, the point is to make the decoder longer than the encoder
decoder_lengths = encoder_inputs_length + 3

# Output projection (convert the internal state vector to character representation)
W = tf.Variable(tf.random_uniform([decoder_hidden_units, vocab_size], -1, 1), dtype=tf.float32)
b = tf.Variable(tf.zeros([vocab_size]), dtype=tf.float32)

# A quick sanity check
assert vocab['EOW'] == 1 and vocab['PAD'] == 0 and vocab['UNK'] == 2

# Setup the input for the decoder
eow_time_slice = tf.ones([batch_size], dtype=tf.int32, name='EOW')
pad_time_slice = tf.zeros([batch_size], dtype=tf.int32, name='PAD')

eow_step_embedded = tf.nn.embedding_lookup(embeddings, eow_time_slice)
pad_step_embedded = tf.nn.embedding_lookup(embeddings, pad_time_slice)

# We create the decoder RNN ourselves and add soft-attention to it
# By defining the behaviour of an RNN cell, an initializer and transition function need to be specified

def loop_fn_initial():
    initial_elements_finished = (0 >= decoder_lengths)
    initial_input = eow_step_embedded
    initial_cell_state = encoder_final_state
    initial_cell_output = None
    initial_loop_state = None
    return (initial_elements_finished,
           initial_input,
           initial_cell_state,
           initial_cell_output,
           initial_loop_state)

def loop_fn_transition(time, previous_output, previous_state, previous_loop_state):
    # soft attention: trivial form of attention
    
    def get_next_input():
        output_logits = tf.add(tf.matmul(previous_output, W), b)
        # THIS IS ATTENTION (the "picking" step is attention: choose what to devote attention to)
        prediction = tf.argmax(output_logits, axis=1)
        next_input = tf.nn.embedding_lookup(embeddings, prediction)
        return next_input
    
    elements_finished = (time >= decoder_lengths)
    
    finished = tf.reduce_all(elements_finished)
    input = tf.cond(finished, lambda: pad_step_embedded, get_next_input)
    
    state = previous_state
    output = previous_output
    loop_state = None
    
    return (elements_finished, input, state, output, loop_state)

# Now we combine both the initializer and transition function
def loop_fn(time, previous_output, previous_state, previous_loop_state):
    if previous_state is None:
        assert previous_output is None and previous_state is None
        return loop_fn_initial()
    else:
        return loop_fn_transition(time, previous_output, previous_state, previous_loop_state)
    
# We can now create the decoder RNN
decoder_outputs_ta, decoder_final_state, _ = tf.nn.raw_rnn(decoder_cell, loop_fn)
decoder_outputs = decoder_outputs_ta.stack()

# Now we convert the state vectors to a human-readable representation using the weights (W) and biases (b) defined earlier
decoder_max_steps, decoder_batch_size, decoder_dim = tf.unstack(tf.shape(decoder_outputs))
decoder_outputs_flat = tf.reshape(decoder_outputs, (-1, decoder_dim))
decoder_logits_flat = tf.add(tf.matmul(decoder_outputs_flat, W), b)
decoder_logits = tf.reshape(decoder_logits_flat, (decoder_max_steps, decoder_batch_size, vocab_size))

# And using this greedy approach, we select the most likely character:
decoder_prediction = tf.argmax(decoder_logits, 2)

# Now we can define the loss and create an optimizer
stepwise_cross_entropy = tf.nn.softmax_cross_entropy_with_logits(
    labels=tf.one_hot(decoder_targets, depth=vocab_size, dtype=tf.float32),
    logits=decoder_logits,
)

loss = tf.reduce_mean(stepwise_cross_entropy)
train_op = tf.train.AdamOptimizer().minimize(loss)

# Setup the session
sess = tf.InteractiveSession()
sess.run(tf.global_variables_initializer())

# A helper function for creating batches of data
def create_batch(inputs, max_sequence_length=None):
    """
    Args:
        inputs:
            list of sentences (integer lists)
        max_sequence_length:
            integer specifying how large should `max_time` dimension be.
            If None, maximum sequence length would be used
    
    Outputs:
        inputs_time_major:
            input sentences transformed into time-major matrix 
            (shape [max_time, batch_size]) padded with 0s
        sequence_lengths:
            batch-sized list of integers specifying amount of active 
            time steps in each input sequence
    """
    
    sequence_lengths = [len(seq) for seq in inputs]
    batch_size = len(inputs)
    
    if max_sequence_length is None:
        max_sequence_length = max(sequence_lengths)
    
    inputs_batch_major = np.zeros(shape=[batch_size, max_sequence_length], dtype=np.int32) # == PAD
    
    for i, seq in enumerate(inputs):
        for j, element in enumerate(seq):
            inputs_batch_major[i, j] = element

    # [batch_size, max_time] -> [max_time, batch_size]
    inputs_time_major = inputs_batch_major.swapaxes(0, 1)

    return inputs_time_major, sequence_lengths
    
# A helper function to convert characters to ids
def word_to_ids(word):
    return [vocab.get(c, vocab['UNK']) for c in word]

# And a helper function to generate a feed dict which converts the data such that it can be fed into the network
def get_feed_dict(words, lengths=None):
    encoder_inputs_, encoder_input_lengths_ = create_batch([word_to_ids(seq) for seq in words])
    decoder_targets_, _ = create_batch([word_to_ids(seq) + [vocab['EOW']] + [vocab['PAD']] * 2 for seq in words])
    if lengths is not None:
        encoder_input_lengths = lengths
    
    return {
        encoder_inputs: encoder_inputs_,
        encoder_inputs_length: encoder_input_lengths_,
        decoder_targets: decoder_targets_
    }
    
# Now we can train!
batch_size = 10
batches_in_epoch = 100
print(len(words) // batch_size)
vocab_inv = {index: word for word, index in vocab.items()}
for repeats in range(3):
    for batch in range(0, len(words) // batch_size):
        i = batch * batch_size
        j = (batch + 1) * batch_size
        fd = get_feed_dict(words[i:j])
        _, l = sess.run([train_op, loss], fd)
        if batch == 0 or batch % batches_in_epoch == 0:
            print('batch {}'.format(batch))
            print('  minibatch loss: {}'.format(sess.run(loss, fd)))
            predict_ = sess.run(decoder_prediction, fd)
            for i, (inp, pred) in enumerate(zip(fd[encoder_inputs].T, predict_.T)):
                inp_txt = ''.join([vocab_inv.get(item, '?') for item in inp if item >= 3])
                pred_txt = ''.join([vocab_inv.get(item, '?') for item in pred if item >= 3])
                print('  sample {}:'.format(i + 1))
                print('    input         > {}'.format(inp))
                print('    predicted     > {}'.format(pred))
                print('    input_txt     > {}'.format(inp_txt))
                print('    predicted_txt > {}'.format(pred_txt))
                if i >= 2:
                    break
            print()