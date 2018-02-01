# Implementation of a rotating buffer on the GPU of size 2.
import threading
import tensorflow as tf
from tensorflow.python.client import timeline
import numpy as np
import time

params = {
    'batch_size': 128,
    'seg_len': 4000,
}

kernel_shape = [64, 8, 100]

graph = tf.Graph()
sess = tf.Session(config=tf.ConfigProto(log_device_placement=False), graph=graph)
verbose = False

target_dev = '/gpu:0'

with graph.as_default(), tf.device('/cpu:0'):

    # Variables
    with tf.device(target_dev):
        var_buffer_out = tf.Variable([[0]], validate_shape=False, dtype=tf.float32, trainable=False)
        var_buffer_in = tf.Variable([0], validate_shape=False, dtype=tf.float32, trainable=False)


    data_in = tf.placeholder(dtype=tf.float32, shape=[None, params['seg_len'], kernel_shape[1]])

    queue = tf.FIFOQueue(shapes=[[params['seg_len'], kernel_shape[1]]],
        dtypes=[tf.float32],
        capacity=2*params['batch_size'],
    )

    enqueue_op = queue.enqueue_many([data_in])
    dequeued_data_in = queue.dequeue_many(params['batch_size'])

    with tf.device(target_dev):
        move_buffer = tf.assign(var_buffer_out, var_buffer_in, validate_shape=False)

        put_in_buffer = tf.assign(var_buffer_in, dequeued_data_in, validate_shape=False)

        get_from_buffer = tf.identity(var_buffer_out)

        with tf.variable_scope("conv1"):
            Wz = tf.get_variable("Wz", initializer=np.zeros(kernel_shape, dtype=np.float32)+0.00001)
            Z = tf.nn.conv1d(get_from_buffer, Wz, 1, 'SAME')
            test_out = (tf.reduce_mean(Z) * 0) + tf.reduce_mean(get_from_buffer)
            if verbose:
                with tf.device('/cpu:0'):
                    test_out = tf.Print(test_out, [put_in_buffer, move_buffer, test_out], '[BUF_IN][BUF_OUT][RESULT]:')

    with tf.control_dependencies([move_buffer]):
        pull = tf.group(put_in_buffer, test_out)


    def runThread(sess, coord):
        i=0
        while not coord.should_stop():
            sess.run(enqueue_op, feed_dict={
                data_in: np.zeros([params['batch_size'], params['seg_len'], kernel_shape[1]], dtype=np.float32)+i
            })
            i += 1

    sess.run(tf.global_variables_initializer())
    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(sess=sess, coord=coord)

    threads = []
    for n in range(1):
        t = threading.Thread(target=runThread, args=(sess, coord))
        t.daemon = True
        t.start()
        threads.append(t)

    # Put something in the input-buffer on the GPU.
    sess.run([put_in_buffer])
    # Move to the output-side of the buffer on the GPU.
    sess.run([move_buffer])

    # Now pull th
    for i in range(20):
        sess.run([pull])

    print('Running a trace..')
    time.sleep(5)  # Give the queue fetcher some time
    run_metadata = tf.RunMetadata()
    sess.run([pull],
        options=tf.RunOptions(trace_level=tf.RunOptions.FULL_TRACE),
        run_metadata=run_metadata
    )
    trace = timeline.Timeline(step_stats=run_metadata.step_stats)
    trace_file = open('timeline.ctf.json', 'w')
    trace_file.write(trace.generate_chrome_trace_format())
    exit() # Trace seems clog thing up?
    # Wrap up
    coord.request_stop()
    coord.join(threads)
    sess.close()