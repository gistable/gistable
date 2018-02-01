import tensorflow as tf
import numpy as np
import pandas as pd
import math

# Data sets
IRIS_TRAINING = "iris_training.csv"
IRIS_TEST = "iris_test.csv"
IRIS_DATA_SIZE = 4
CLASS_SIZE = 3

# load csv data for iris data format
def load_csv(filename):
    file = pd.read_csv(filename, header=0)

    # get sample's metadata
    n_samples = int(file.columns[0])
    n_features = int(file.columns[1])

    # divide samples into explanation variables and target variable
    data = np.empty((n_samples, n_features))
    target = np.empty((n_samples,), dtype=np.int)
    for i, row in enumerate(file.itertuples()):
        target[i] = np.asarray(row[-1], dtype=np.int)
        data[i] = np.asarray(row[1:n_features+1], dtype=np.float64)
    return (data, target)

# output train data 
def get_batch_data(x_train, y_train, size=None):
    if size is None:
        size = len(x_train)
    batch_xs = x_train
    batch_ys = []

    # convert to 1-of-N vector
    for i in range(len(y_train)):
        val = np.zeros((3), dtype=np.float64)
        val[y_train[i]] = 1.0
        batch_ys.append(val)
    batch_ys = np.asarray(batch_ys)
    return batch_xs[:size], batch_ys[:size]

# output test data
def get_test_data(x_test, y_test):
    batch_ys = []

    # convert to 1-of-N vector
    for i in range(len(y_test)):
        val = np.zeros((3), dtype=np.float64)
        val[y_test[i]] = 1.0
        batch_ys.append(val)
    return x_test, np.asarray(batch_ys)

# for parameter initialize
def get_stddev(in_dim, out_dim):
    return 1.3 / math.sqrt(float(in_dim) + float(out_dim))

# DNN Model Class
class Classifier:
    def __init__(self, hidden_units=[10], n_classes=0):
        self._hidden_units = hidden_units
        self._n_classes = n_classes
        self._sess = tf.Session()

    # build model
    def inference(self, x):
        hidden = []

        # Input Layer
        with tf.name_scope("input"):
            weights = tf.Variable(tf.truncated_normal([IRIS_DATA_SIZE, self._hidden_units[0]], stddev=get_stddev(IRIS_DATA_SIZE, self._hidden_units[0])), name='weights')
            biases = tf.Variable(tf.zeros([self._hidden_units[0]]), name='biases')
            input = tf.matmul(x, weights) + biases

        # Hidden Layers
        for index, num_hidden in enumerate(self._hidden_units):
            if index == len(self._hidden_units) - 1: break
            with tf.name_scope("hidden{}".format(index+1)):
                weights = tf.Variable(tf.truncated_normal([num_hidden, self._hidden_units[index+1]], stddev=get_stddev(num_hidden, self._hidden_units[index+1])), name='weights')
                biases = tf.Variable(tf.zeros([self._hidden_units[index+1]]), name='biases')
                inputs = input if index == 0 else hidden[index-1]
                hidden.append(tf.nn.relu(tf.matmul(inputs, weights) + biases, name="hidden{}".format(index+1)))
        
        # Output Layer
        with tf.name_scope('output'):
            weights = tf.Variable(tf.truncated_normal([self._hidden_units[-1], self._n_classes], stddev=get_stddev(self._hidden_units[-1], self._n_classes)), name='weights')
            biases = tf.Variable(tf.zeros([self._n_classes]), name='biases')
            logits = tf.nn.softmax(tf.matmul(hidden[-1], weights) + biases)

        return logits

    # loss function
    def loss(self, logits, y):        
        return -tf.reduce_mean(y * tf.log(logits))

    # fitting function for train data
    def fit(self, x_train=None, y_train=None, steps=200):
        # build model
        x = tf.placeholder(tf.float32, [None, IRIS_DATA_SIZE])
        y = tf.placeholder(tf.float32, [None, CLASS_SIZE])
        logits = self.inference(x)
        loss = self.loss(logits, y)
        train_op = tf.train.GradientDescentOptimizer(0.5).minimize(loss)

        # save variables
        self._x = x
        self._y = y
        self._logits = logits
 
        # init parameters
        init = tf.initialize_all_variables() 
        self._sess.run(init)

        # train
        for i in range(steps):
            batch_xs, batch_ys = get_batch_data(x_train, y_train)
            self._sess.run(train_op, feed_dict={x: batch_xs, y: batch_ys})

    # evaluation function for test data
    def evaluate(self, x_test=None, y_test=None):
        x_test, y_test = get_test_data(x_test, y_test)
        
        # build accuracy calculate step
        correct_prediction = tf.equal(tf.argmax(self._logits, 1), tf.argmax(self._y, 1))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

        # evaluate
        return self._sess.run([accuracy], feed_dict={self._x: x_test, self._y: y_test})

    # label pridiction
    def predict(self, samples):
        predictions = tf.argmax(self._logits, 1)
        return self._sess.run(predictions, {self._x: samples})

def main(args):
    # Load datasets.
    x_train, y_train = load_csv(filename=IRIS_TRAINING)
    x_test, y_test = load_csv(filename=IRIS_TEST)

    # Build 3 layer DNN with 10, 20, 10 units respectively.
    classifier = Classifier(hidden_units=[10, 20, 10], n_classes=CLASS_SIZE)

    # Fit model.
    classifier.fit(x_train, y_train, steps=200)

    # Evaluate accuracy.
    accuracy_score = classifier.evaluate(x_test, y_test)[0]
    print('Accuracy: {0:f}'.format(accuracy_score))

    # Classify two new flower samples.
    new_samples = np.array([[6.4, 3.2, 4.5, 1.5], [5.8, 3.1, 5.0, 1.7]], dtype=float)
    y = classifier.predict(new_samples)
    print ('Predictions: {}'.format(str(y)))

if __name__ == '__main__':
  tf.app.run()