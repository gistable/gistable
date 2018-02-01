# -*- coding: utf-8 -*-
# Usage: python view-graph.py graph.pb
import sys
import tensorflow as tf
from os.path import isfile
from tensorflow.python.platform import gfile
import webbrowser
from subprocess import Popen
import time

model_filename = sys.argv[1]
if not isfile(model_filename):
    print("%s not found" % model_filename)
    exit()
with tf.Session() as sess:
    with gfile.FastGFile(model_filename, 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        g_in = tf.import_graph_def(graph_def)
LOGDIR = model_filename + "-run"
train_writer = tf.summary.FileWriter(LOGDIR)
train_writer.add_graph(sess.graph)

p = Popen(['python', '-m', 'tensorflow.tensorboard', '--logdir', LOGDIR])
time.sleep(2)
webbrowser.open("http://127.0.0.1:6006/#graphs")
try:
    while True:
        time.sleep(60 * 60 * 24)
except KeyboardInterrupt:
    p.terminate()