import collections, math, random, numpy
import tensorflow as tf
from sklearn.cross_validation import train_test_split

sentences = """hated the movie it was stupid;\ni hated it so boring;\nawesome the movie was inspiring;\nhated it what a disaster;\nwe hated the movie they were idiotic;\nhe was stupid, hated her;\nstupid movie is boring;\ninspiring ourselves, awesome;\ninspiring me, brilliant;\nwe hated it they were rubbish;\nany inspiring movie is amazing;\nit was stupid what a disaster;\nits stupid, rubbish;\nstupid, idiotic!;\nawesome great movie;\nboring, must be hated;\nhe was boring the movie was stupid;\nboring movie was a disaster;\nboth boring and rubbish;\nso boring and idiotic;\ngreat to amazing;\ndisaster, more than hated;\nbetween disaster and stupid;\ndisaster, so boring;\nawesome movie, brilliant;\ntoo awesome she was amazing;\nhe was brilliant loved it;\ndisaster, only idiotic;\nrubbish movie hated him;\nit was rubbish, why so stupid?;\nrubbish, too boring;\nrubbish, disaster!;\nrubbish, very idiotic;\nidiotic movie hated it;\nshe was idiotic, so stupid;\nidiotic movie, it was boring;\nit was idiotic, movie was a disaster;\nidiotic and rubbish;\nI loved it, it was awesome;\nhe was stupid, hated her;\nbrilliant, loved it;\nloved the movie amazing;\nit was great loved the movie;\nmovie was great, inspiring;\ngreat movie, awesome;\nthey were great, brilliant;\ngreat amazing!;\nThey were inspiring loved it;\ninspiring movie great;\nawesome loved it;\nthey were brilliant great movie;\nshe was brilliant the movie was inspiring;\nhe was brilliant between them they were awesome;\nbrilliant, above amazing;\njust amazing loved it;\ndisaster, o what rubbish;\nabove amazing beyond inspiring;\nso amazing movie was awesome;\namazing brilliant movie;"""
words = [word for word in sentences.replace(';', '').replace('!', '').replace('?', '').replace(',', '').lower().split() if word.lower() not in ['it', 'movie', 'the' 'was', 'were', 'so', 'a', 'i', 'he', 'her', 'me', 'any', 'its', 'be', 'they', 'and']]
vocabulary_size = 15

def build_dataset(words):
  count = [['UNK', -1]]
  count.extend(collections.Counter(words).most_common(vocabulary_size - 1))
  dictionary = dict()
  for word, _ in count:
    dictionary[word] = len(dictionary)
  data = list()
  for word in words:
    if word in dictionary:
      index = dictionary[word]
    else:
      index = 0
    data.append(index)
  return data, dictionary

data, dictionary = build_dataset(words)
data_index = 0

def generate_batch(batch_size, num_skips, skip_window):
  global data_index
  batch = numpy.ndarray(shape=(batch_size), dtype=numpy.int32)
  labels = numpy.ndarray(shape=(batch_size, 1), dtype=numpy.int32)
  span = 2 * skip_window + 1
  buffer = collections.deque(maxlen=span)
  for _ in range(span):
    buffer.append(data[data_index])
    data_index = (data_index + 1) % len(data)
  for i in range(batch_size // num_skips):
    target = skip_window
    targets_to_avoid = [skip_window]
    for j in range(num_skips):
      while target in targets_to_avoid:
        target = random.randint(0, span - 1)
      targets_to_avoid.append(target)
      batch[i * num_skips + j] = buffer[skip_window]
      labels[i * num_skips + j, 0] = buffer[target]
    buffer.append(data[data_index])
    data_index = (data_index + 1) % len(data)
  return batch, labels

batch_size = 20
embedding_size = 4
skip_window = 3
num_skips = 2
valid_size = 4
valid_window = 10
valid_examples = numpy.random.choice(valid_window, valid_size, replace=False)
num_sampled = 6


graph = tf.Graph()
with graph.as_default():
  train_inputs = tf.placeholder(tf.int32, shape=[batch_size])
  train_labels = tf.placeholder(tf.int32, shape=[batch_size, 1])
  valid_dataset = tf.constant(valid_examples, dtype=tf.int32)
  with tf.device('/cpu:0'):
    embeddings = tf.Variable(
        tf.random_uniform([vocabulary_size, embedding_size], -1.0, 1.0))
    embed = tf.nn.embedding_lookup(embeddings, train_inputs)
    nce_weights = tf.Variable(
        tf.truncated_normal([vocabulary_size, embedding_size],
                            stddev=1.0 / math.sqrt(embedding_size)))
    nce_biases = tf.Variable(tf.zeros([vocabulary_size]))
    loss = tf.reduce_mean(
      tf.nn.nce_loss(nce_weights, nce_biases, embed, train_labels,
                     num_sampled, vocabulary_size))
  optimizer = tf.train.GradientDescentOptimizer(1.0).minimize(loss)
  norm = tf.sqrt(tf.reduce_sum(tf.square(embeddings), 1, keep_dims=True))
  normalized_embeddings = embeddings / norm
  valid_embeddings = tf.nn.embedding_lookup(
      normalized_embeddings, valid_dataset)
  similarity = tf.matmul(
      valid_embeddings, normalized_embeddings, transpose_b=True)
  init = tf.global_variables_initializer()

with tf.Session(graph=graph) as session:
  init.run()
  average_loss = 0
  for step in range(10001):
    batch_inputs, batch_labels = generate_batch(batch_size, num_skips, skip_window)
    feed_dict = {train_inputs: batch_inputs, train_labels: batch_labels}
    _, loss_val, normalized_embeddings_np = session.run([optimizer, loss, normalized_embeddings], feed_dict=feed_dict)
    average_loss += loss_val
  final_embeddings = normalized_embeddings.eval()

neg_sent="""hated the movie it was stupid;\ni hated it so boring;\nhated it what a disaster;\nwe hated it they were rubbish;\nwe hated the movie they were idiotic;\nhe was stupid, hated her;\nstupid movie is boring;\nit was stupid what a disaster;\nits stupid, rubbish;\nstupid, idiotic!;""".replace(';', '').replace('!', '').replace('?', '').replace(',', '').lower().split('\n')
pos_sent="""I loved it, it was awesome;\nbrilliant, loved it;\nloved the movie amazing;\nit was great loved the movie;\nmovie was great, inspiring;\ngreat movie, awesome;\nthey were great, brilliant;\ngreat amazing!;\nThey were inspiring loved it;\ninspiring movie great;""".replace(';', '').replace('!', '').replace('?', '').replace(',', '').lower().split('\n')

x_sent = numpy.zeros((len(pos_sent + neg_sent), embedding_size), dtype=numpy.float)
y_sent = numpy.zeros((len(pos_sent + neg_sent), 2), dtype=numpy.int)

for i, sent in enumerate(pos_sent):
  y_sent[i, 0] = 1
  x_sent[i] = numpy.average([final_embeddings[dictionary[word]] for word in sent.split() if word in dictionary], axis=0)

for i, sent in enumerate(neg_sent):
  y_sent[len(pos_sent) + i, 1] = 1
  x_sent[len(pos_sent) + i] = numpy.average([final_embeddings[dictionary[word]] for word in sent.split() if word in dictionary], axis=0)

train_X, test_X, train_y, test_y = train_test_split(x_sent, y_sent, test_size=0.10, random_state=42)

x_size = embedding_size
y_size = 2
h_size = 4


X = tf.placeholder("float", shape=[None, x_size])
y = tf.placeholder("float", shape=[None, y_size])
w_1 = tf.Variable(tf.random_normal((x_size, h_size), stddev=0.1))
w_2 = tf.Variable(tf.random_normal((h_size, y_size), stddev=0.1))
h = tf.nn.sigmoid(tf.matmul(X, w_1))
yhat = tf.matmul(h, w_2)
predict = tf.argmax(yhat, dimension=1)
cost    = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(yhat, y))
updates = tf.train.GradientDescentOptimizer(0.01).minimize(cost)
sess = tf.InteractiveSession()
init = tf.initialize_all_variables()
sess.run(init)

for epoch in range(1000):
    for i in range(len(train_X)):
        sess.run(updates, feed_dict={X: train_X[i: i + 1], y: train_y[i: i + 1]})
    train_accuracy = numpy.mean(numpy.argmax(train_y, axis=1) == sess.run(predict, feed_dict={X: train_X, y: train_y}))
    test_accuracy  = numpy.mean(numpy.argmax(test_y, axis=1) == sess.run(predict, feed_dict={X: test_X, y: test_y}))
    print("Epoch = %d, train accuracy = %.2f%%, test accuracy = %.2f%%" % (epoch + 1, 100. * train_accuracy, 100. * test_accuracy))

sess.close()