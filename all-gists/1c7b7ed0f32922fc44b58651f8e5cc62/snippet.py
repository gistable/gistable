

# Initialize placeholders for feeding in to the queue
pl_queue_screens = tf.placeholder(tf.float32, shape=[config.seq_length, config.image_size, config.image_size, config.input_channels], name="queue_inputs")
pl_queue_targets = tf.placeholder(tf.uint8, shape=[config.seq_length], name="queue_targets_cnt")

#  ...

capacity = config.min_after_dequeue + 10 * (config.num_gpus*config.batch_size)
q = tf.RandomShuffleQueue(
    capacity=capacity,
    min_after_dequeue=config.min_after_dequeue,
    dtypes=[tf.float32, tf.uint8],
    shapes=[[config.seq_length, config.image_size, config.image_size, config.input_channels], [config.seq_length]]
)


# ..and finally the enqueue operation for adding a single sequence
enqueue_op = q.enqueue([seq_proc, pl_queue_targets])

# Misc queue operations
examples_in_queue = q.size()
queue_close_op = q.close(cancel_pending_enqueues=True)

# This must be the input for the training operation
inputs_batch_queue, targets_batch_queue = q.dequeue_many(config.batch_size)

# Placeholders for training and evaluation
batch_screens = tf.placeholder_with_default(inputs_batch_queue, [None, config.seq_length, config.image_size, config.image_size, config.input_channels], name="model_inputs")
batch_targets = tf.placeholder_with_default(targets_batch_queue, [None, config.seq_length], name="model_targets_cnt")
dropout_keep_prob = tf.placeholder_with_default(tf.constant(1.0), shape=[], name="dropout_keep_prob")

# ...

########################################################################################################
########################################################################################################
########################################################################################################

# Now we start a number of threads that read from disk (numpy) array and feed it to the queue
# Coordinator for threads
coord = tf.train.Coordinator()

# Start the data loading + preprocessing threads
threads = []
for _ in range(config.num_preproc_threads):
	
	# This is the method that runs in the threads and feeds examples to the queue
    t = threading.Thread(target=load_preproc_enqueue_thread, args=(
        sess, coord, enqueue_op, pl_queue_screens, pl_queue_targets,
    	# additional arguments ...     
    ))

    t.setDaemon(True)
    t.start()
    threads.append(t)
    coord.register_thread(t)
    time.sleep(0.5)

num_examples_in_queue = sess.run(examples_in_queue)
while num_examples_in_queue < config.min_after_dequeue:
    num_examples_in_queue = sess.run(examples_in_queue)
    for t in threads:
        if not t.isAlive():
            coord.request_stop()
            raise ValueError("One or more enqueuing threads crashed...")

    print("Filling up queue with training examples: %i/%i" % (num_examples_in_queue, config.min_after_dequeue))
    time.sleep(1)

# ...

########################################################################################################
########################################################################################################
########################################################################################################

# ...
# For your training operation use batch_screens and batch_targets as inputs
# Look at the use of tf.placeholder_with_default() => if no feed_dict{} is fed in then the placeholder will fetch examples from the queue
# For your validation data, you can just use the placeholders/feeddict.


########################################################################################################


def load_preproc_enqueue_thread(sess, coord, enqueue_op, pl_queue_screens, pl_queue_targets):
	
	# MODIFY THIS FUNCTION FOR LOADING SLICES FROM YOUR INPUT TENSOR AND FEEDING INTO QUEUE PLACEHOLDERS

    # Fetch the HDF5 files from disk...
    filenames_queue = glob.glob(os.path.join(dataset_path, "train/*.h5"))
    filenames_queue.sort()

    while not coord.should_stop():

        # Shuffle the filenames each time we have fed everything
        random.shuffle(filenames_queue)

        for filename in filenames_queue:

            # Read 100 examples from HDF5 file, shuffle files within file.
            # Optionally also perform mean subtraction and normalization.
            # Sequences can also be tiled if the examples are padded with zeros
            # after one cycle length.
            screens, _, count_labels, cycle_lengths, residual_frames, _ = \
                read_examples_from_hdf5(
                    filename, shuffle=True, data_whitening=data_whitening,
                    expand_dims=expand_dims, convert_to_grayscale=convert_to_grayscale
                )

            # Feed Dictionary without the labels
            feed_dict = {
                pl_queue_screens: screens[index,],
                pl_queue_targets: targets,
                pl_flip_image: random_flip,
                pl_brightness_delta: random_brightness_delta,
                pl_contrast_factor: random_contrast_factor
            }

            # Feed examples to the queue
            try:
                sess.run(enqueue_op, feed_dict=feed_dict)
            except tf.errors.CancelledError:
                return

