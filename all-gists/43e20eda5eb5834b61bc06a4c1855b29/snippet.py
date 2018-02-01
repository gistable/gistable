import operator
import threading
from functools import reduce

import keras
import keras.backend as K
from keras.engine import Model
import numpy as np
import tensorflow as tf
import time
from keras.layers import Conv2D
from tqdm import tqdm


def prod(factors):
    return reduce(operator.mul, factors, 1)


TRAINING = True
with K.get_session() as sess:
    shp = [10, 200, 200, 3]
    shp1 = [10, 7, 7, 80]
    inp = K.placeholder(shp)
    inp1 = K.placeholder(shp1)
    queue = tf.FIFOQueue(20, [tf.float32, tf.float32], [shp, shp1])
    x1, y1 = queue.dequeue()
    enqueue = queue.enqueue([inp, inp1])
    model = keras.applications.ResNet50(False, "imagenet", x1, shp[1:])
    for i in range(3):
        model.layers.pop()
        model.layers[-1].outbound_nodes = []
        model.outputs = [model.layers[-1].output]
    output = model.outputs[0]  # 7x7
    # Reduce filter size to avoid OOM
    output = Conv2D(32, (1, 1), padding="same", activation='relu')(output)
    output3 = Conv2D(5 * (4 + 11 + 1), (1, 1), padding="same", activation='relu')(
        output)  # YOLO output B (4 + nb_class +1)
    cost = tf.reduce_sum(tf.abs(output3 - y1))
    optimizer = tf.train.RMSPropOptimizer(0.001).minimize(cost)
    sess.run(tf.global_variables_initializer())


    def get_input():
        # Super long processing I/O bla bla bla
        return np.arange(prod(shp)).reshape(shp).astype(np.float32), np.arange(prod(shp1)).reshape(shp1).astype(
            np.float32)


    def genera(coord, enqueue_op):
        while not coord.should_stop():
            inp_feed, inp1_feed = get_input()
            sess.run(enqueue_op, feed_dict={inp: inp_feed, inp1: inp1_feed})


    start = time.time()
    for i in tqdm(range(10)):  # EPOCH
        for j in range(30):  # Batch
            x,y = get_input()
            optimizer_, s = sess.run([optimizer, queue.size()], feed_dict={x1:x,y1:y,K.learning_phase(): int(TRAINING)})
    print("Took : ", time.time() - start)


    coordinator = tf.train.Coordinator()
    threads = [threading.Thread(target=genera, args=(coordinator, enqueue)) for i in range(10)]
    for t in threads:
        t.start()
    start = time.time()
    for i in tqdm(range(10)):  # EPOCH
        for j in range(30):  # Batch
            optimizer_, s = sess.run([optimizer, queue.size()], feed_dict={K.learning_phase(): int(TRAINING)})
    print("Took : ", time.time() - start)

    def clear_queue(queue, threads):
        while any([t.is_alive() for t in threads]):
            _, s = sess.run([queue.dequeue(), queue.size()])
            print(s)


    coordinator.request_stop()
    clear_queue(queue, threads)

    coordinator.join(threads)
    print("DONE Queue")


