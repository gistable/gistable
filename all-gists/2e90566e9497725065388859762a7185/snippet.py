import tensorflow as tf
import numpy as np

from create_sentiment_featuresets import create_feature_sets_and_labels

train_x, train_y, test_x, test_y = create_feature_sets_and_labels('pos.txt', 'neg.txt')



n_nodes_h11 = 500
n_nodes_h12 = 500
n_nodes_h13 = 500

all_nodes = [len(train_x[0]), n_nodes_h11, n_nodes_h12, n_nodes_h13]

n_classes = 2
batch_size = 100

x = tf.placeholder('float', [None, len(train_x[0])])
y = tf.placeholder('float')


def neural_network_model(data, nodes, classes, num_layers):
    num_layers -= 1
    if num_layers > 0:
        if len(nodes) > 1:
            layer = {'weights':tf.Variable(tf.random_normal([nodes[0], nodes[1]])),
                     'biases':tf.Variable(tf.random_normal([nodes[1]]))}
            
            l = tf.add(tf.matmul(data,layer['weights']),layer['biases'])
            l = tf.nn.relu(l)
            return neural_network_model(l, nodes[1:len(nodes)], classes, num_layers)
        else:
            layer = {'weights':tf.Variable(tf.random_normal([nodes[0], classes])),
                     'biases':tf.Variable(tf.random_normal([classes]))}
            
            l = tf.add(tf.matmul(data,layer['weights']),layer['biases'])
            l = tf.nn.relu(l)
            return neural_network_model(l, nodes, classes, num_layers)
    else:
        output_layer = {'weights':tf.Variable(tf.random_normal([nodes[0], classes])),
                        'biases':tf.Variable(tf.random_normal([classes]))}
        output = tf.matmul(data, output_layer['weights']) + output_layer['biases']
        return output


def train_neural_network(x):
    prediction = neural_network_model(x, all_nodes, n_classes, len(all_nodes))
    cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=prediction, labels=y))
    optimizer = tf.train.AdamOptimizer().minimize(cost)

    hm_epochs = 20

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())

        for epoch in range(hm_epochs):
            epoch_loss = 0

            i = 0
            while i < len(train_x):
                start = i
                end = i + batch_size

                batch_x = np.array(train_x[start:end])
                batch_y = np.array(train_y[start:end])

                _, c = sess.run([optimizer, cost], feed_dict={x: batch_x, y: batch_y})
                epoch_loss += c
                i += batch_size

            print('Epoch', epoch+1, 'completed out of', hm_epochs, 'loss:', epoch_loss)

        correct = tf.equal(tf.argmax(prediction,1), tf.argmax(y,1))
        accuracy = tf.reduce_mean(tf.cast(correct, 'float'))
        print('Accuracy:', accuracy.eval({x:test_x, y:test_y}))



train_neural_network(x)
