""" 
Play with saving .

Closest:
    https://github.com/tensorflow/tensorflow/issues/616#issuecomment-205620223
"""
import numpy as np

import tensorflow as tf
from tensorflow.python.platform import gfile
# from tensorflow.python.training.training_util import write_graph
# from tensorflow.python.tools.freeze_graph import freeze_graph
from tensorflow.python.framework.graph_util import convert_variables_to_constants


def create_graph():
    g = tf.Graph()
    with g.as_default():
        # compute graph
        input_ = tf.placeholder(tf.float32, [10], name="input")
        parameter = tf.Variable(initial_value=[2.0]*10, name="parameter", trainable=True)
        output_ = tf.add(input_, parameter, name="output")

        # initializers
        local_init_op = tf.local_variables_initializer()
        global_init_op = tf.global_variables_initializer()

        # gets all variables in the graph
        saver = tf.train.Saver()

        # save to collection so can access later
        tf.add_to_collection(input_.name, input_)
        tf.add_to_collection(output_.name, output_)

    return g, saver, (input_, output_, local_init_op, global_init_op)


def run_graph(g, *ops):
    input_, output_, local_init_op, global_init_op = ops

    sess = tf.Session(graph=g)
    sess.run([local_init_op, global_init_op])
    output = sess.run(output_, feed_dict={input_: np.arange(10, dtype=np.float32)})
    print "output", output

    return sess


def save_graph(sess, saver):
    saver.save(sess, "./tmp/model", write_meta_graph=True, global_step=1)

    with open("./tmp/" + "graph.pb", 'wb') as f:
        f.write(sess.graph_def.SerializeToString())
    sess.close()


def load_graph(load_type="restore"):
    checkpoint_path = tf.train.latest_checkpoint("./tmp/")

    if load_type == "build_graph":
        g, saver, ops = create_graph()
        input_, output_, local_init_op, global_init_op = ops

        with tf.Session(graph=g) as sess:
            saver.restore(sess, checkpoint_path)

            output = sess.run(output_, feed_dict={input_: np.arange(10, dtype=np.float32)})
            print "output", output

            freeze_graph(sess)

    elif load_type == "import_meta_graph":
        saver = tf.train.import_meta_graph(checkpoint_path + ".meta", import_scope=None)
        with tf.Session() as sess:
            saver.restore(sess, checkpoint_path)
            input_ = tf.get_collection("input:0", scope="")[0]
            output_ = tf.get_collection("output:0", scope="")[0]

            output = sess.run(output_, feed_dict={input_: np.arange(10, dtype=np.float32)})
            print "output", output

            # -- this works too
            output = sess.run("output:0", feed_dict={"input:0": np.arange(10, dtype=np.float32)})
            print "output", output

            freeze_graph(sess)

    else:
        raise ValueError("Wrong load_type.")


def freeze_graph(sess):
    # convert_variables_to_constants(sess, input_graph_def, output_node_names, variable_names_whitelist=None)
    with gfile.FastGFile("./tmp/" + "graph.pb", 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())

    frozen_graph_def = convert_variables_to_constants(sess, graph_def, ["output"])

    with tf.gfile.GFile("./tmp/" + "frozen.pb", "wb") as f:
        f.write(frozen_graph_def.SerializeToString())

    return frozen_graph_def


def load_frozen_graph():
    filename = "./tmp/" + "frozen.pb"

    with tf.gfile.GFile(filename, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())

    with tf.Graph().as_default() as graph:
        new_input = tf.placeholder(tf.float32, [10], name="new_input")

        tf.import_graph_def(
            graph_def,
            # usually, during training you use queues, but at inference time use placeholders
            # this turns into "input
            input_map={"input:0": new_input},
            return_elements=None,
            # if input_map is not None, needs a name
            name="bla",
            op_dict=None,
            producer_op_list=None
        )

    checkpoint_path = tf.train.latest_checkpoint("./tmp/")

    with tf.Session(graph=graph) as sess:
        saver = tf.train.import_meta_graph(checkpoint_path + ".meta", import_scope=None)
        saver.restore(sess, checkpoint_path)

        output = sess.run("output:0", feed_dict={"input:0": np.arange(10, dtype=np.float32)})
        print "output", output


if __name__ == '__main__':
    import sys

    if len(sys.argv) == 2:
        _, load_type = sys.argv
    else:
        load_type = "build_graph"

    # -- multiple graphs?
    g, saver, ops = create_graph()
    sess = run_graph(g, *ops)
    save_graph(sess, saver)
    load_graph(load_type=load_type)
    load_frozen_graph()
