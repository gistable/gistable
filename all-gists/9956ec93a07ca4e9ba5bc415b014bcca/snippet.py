"""Script to illustrate usage of tf.estimator.Estimator in TF v1.3"""
import tensorflow as tf

from tensorflow.examples.tutorials.mnist import input_data as mnist_data
from tensorflow.contrib import slim
from tensorflow.contrib.learn import ModeKeys
from tensorflow.contrib.learn import learn_runner


# Show debugging output
tf.logging.set_verbosity(tf.logging.DEBUG)

# Set default flags for the output directories
FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string(
    flag_name='model_dir', default_value='./mnist_training',
    docstring='Output directory for model and training stats.')
tf.app.flags.DEFINE_string(
    flag_name='data_dir', default_value='./mnist_data',
    docstring='Directory to download the data to.')


# Define and run experiment ###############################
def run_experiment(argv=None):
    """Run the training experiment."""
    # Define model parameters
    params = tf.contrib.training.HParams(
        learning_rate=0.002,
        n_classes=10,
        train_steps=5000,
        min_eval_frequency=100
    )

    # Set the run_config and the directory to save the model and stats
    run_config = tf.contrib.learn.RunConfig()
    run_config = run_config.replace(model_dir=FLAGS.model_dir)

    learn_runner.run(
        experiment_fn=experiment_fn,  # First-class function
        run_config=run_config,  # RunConfig
        schedule="train_and_evaluate",  # What to run
        hparams=params  # HParams
    )


def experiment_fn(run_config, params):
    """Create an experiment to train and evaluate the model.

    Args:
        run_config (RunConfig): Configuration for Estimator run.
        params (HParam): Hyperparameters

    Returns:
        (Experiment) Experiment for training the mnist model.
    """
    # You can change a subset of the run_config properties as
    run_config = run_config.replace(
        save_checkpoints_steps=params.min_eval_frequency)
    # Define the mnist classifier
    estimator = get_estimator(run_config, params)
    # Setup data loaders
    mnist = mnist_data.read_data_sets(FLAGS.data_dir, one_hot=False)
    train_input_fn, train_input_hook = get_train_inputs(
        batch_size=128, mnist_data=mnist)
    eval_input_fn, eval_input_hook = get_test_inputs(
        batch_size=128, mnist_data=mnist)
    # Define the experiment
    experiment = tf.contrib.learn.Experiment(
        estimator=estimator,  # Estimator
        train_input_fn=train_input_fn,  # First-class function
        eval_input_fn=eval_input_fn,  # First-class function
        train_steps=params.train_steps,  # Minibatch steps
        min_eval_frequency=params.min_eval_frequency,  # Eval frequency
        train_monitors=[train_input_hook],  # Hooks for training
        eval_hooks=[eval_input_hook],  # Hooks for evaluation
        eval_steps=None  # Use evaluation feeder until its empty
    )
    return experiment


# Define model ############################################
def get_estimator(run_config, params):
    """Return the model as a Tensorflow Estimator object.

    Args:
         run_config (RunConfig): Configuration for Estimator run.
         params (HParams): hyperparameters.
    """
    return tf.estimator.Estimator(
        model_fn=model_fn,  # First-class function
        params=params,  # HParams
        config=run_config  # RunConfig
    )


def model_fn(features, labels, mode, params):
    """Model function used in the estimator.

    Args:
        features (Tensor): Input features to the model.
        labels (Tensor): Labels tensor for training and evaluation.
        mode (ModeKeys): Specifies if training, evaluation or prediction.
        params (HParams): hyperparameters.

    Returns:
        (EstimatorSpec): Model to be run by Estimator.
    """
    is_training = mode == ModeKeys.TRAIN
    # Define model's architecture
    logits = architecture(features, is_training=is_training)
    predictions = tf.argmax(logits, axis=-1)
    # Loss, training and eval operations are not needed during inference.
    loss = None
    train_op = None
    eval_metric_ops = {}
    if mode != ModeKeys.INFER:
        loss = tf.losses.sparse_softmax_cross_entropy(
            labels=tf.cast(labels, tf.int32),
            logits=logits)
        train_op = get_train_op_fn(loss, params)
        eval_metric_ops = get_eval_metric_ops(labels, predictions)
    return tf.estimator.EstimatorSpec(
        mode=mode,
        predictions=predictions,
        loss=loss,
        train_op=train_op,
        eval_metric_ops=eval_metric_ops
    )


def get_train_op_fn(loss, params):
    """Get the training Op.

    Args:
         loss (Tensor): Scalar Tensor that represents the loss function.
         params (HParams): Hyperparameters (needs to have `learning_rate`)

    Returns:
        Training Op
    """
    return tf.contrib.layers.optimize_loss(
        loss=loss,
        global_step=tf.contrib.framework.get_global_step(),
        optimizer=tf.train.AdamOptimizer,
        learning_rate=params.learning_rate
    )


def get_eval_metric_ops(labels, predictions):
    """Return a dict of the evaluation Ops.

    Args:
        labels (Tensor): Labels tensor for training and evaluation.
        predictions (Tensor): Predictions Tensor.
    Returns:
        Dict of metric results keyed by name.
    """
    return {
        'Accuracy': tf.metrics.accuracy(
            labels=labels,
            predictions=predictions,
            name='accuracy')
    }


def architecture(inputs, is_training, scope='MnistConvNet'):
    """Return the output operation following the network architecture.

    Args:
        inputs (Tensor): Input Tensor
        is_training (bool): True iff in training mode
        scope (str): Name of the scope of the architecture

    Returns:
         Logits output Op for the network.
    """
    with tf.variable_scope(scope):
        with slim.arg_scope(
                [slim.conv2d, slim.fully_connected],
                weights_initializer=tf.contrib.layers.xavier_initializer()):
            net = slim.conv2d(inputs, 20, [5, 5], padding='VALID',
                              scope='conv1')
            net = slim.max_pool2d(net, 2, stride=2, scope='pool2')
            net = slim.conv2d(net, 40, [5, 5], padding='VALID',
                              scope='conv3')
            net = slim.max_pool2d(net, 2, stride=2, scope='pool4')
            net = tf.reshape(net, [-1, 4 * 4 * 40])
            net = slim.fully_connected(net, 256, scope='fn5')
            net = slim.dropout(net, is_training=is_training,
                               scope='dropout5')
            net = slim.fully_connected(net, 256, scope='fn6')
            net = slim.dropout(net, is_training=is_training,
                               scope='dropout6')
            net = slim.fully_connected(net, 10, scope='output',
                                       activation_fn=None)
        return net


# Define data loaders #####################################
class IteratorInitializerHook(tf.train.SessionRunHook):
    """Hook to initialise data iterator after Session is created."""

    def __init__(self):
        super(IteratorInitializerHook, self).__init__()
        self.iterator_initializer_func = None

    def after_create_session(self, session, coord):
        """Initialise the iterator after the session has been created."""
        self.iterator_initializer_func(session)


# Define the training inputs
def get_train_inputs(batch_size, mnist_data):
    """Return the input function to get the training data.

    Args:
        batch_size (int): Batch size of training iterator that is returned
                          by the input function.
        mnist_data (Object): Object holding the loaded mnist data.

    Returns:
        (Input function, IteratorInitializerHook):
            - Function that returns (features, labels) when called.
            - Hook to initialise input iterator.
    """
    iterator_initializer_hook = IteratorInitializerHook()

    def train_inputs():
        """Returns training set as Operations.

        Returns:
            (features, labels) Operations that iterate over the dataset
            on every evaluation
        """
        with tf.name_scope('Training_data'):
            # Get Mnist data
            images = mnist_data.train.images.reshape([-1, 28, 28, 1])
            labels = mnist_data.train.labels
            # Define placeholders
            images_placeholder = tf.placeholder(
                images.dtype, images.shape)
            labels_placeholder = tf.placeholder(
                labels.dtype, labels.shape)
            # Build dataset iterator
            dataset = tf.contrib.data.Dataset.from_tensor_slices(
                (images_placeholder, labels_placeholder))
            dataset = dataset.repeat(None)  # Infinite iterations
            dataset = dataset.shuffle(buffer_size=10000)
            dataset = dataset.batch(batch_size)
            iterator = dataset.make_initializable_iterator()
            next_example, next_label = iterator.get_next()
            # Set runhook to initialize iterator
            iterator_initializer_hook.iterator_initializer_func = \
                lambda sess: sess.run(
                    iterator.initializer,
                    feed_dict={images_placeholder: images,
                               labels_placeholder: labels})
            # Return batched (features, labels)
            return next_example, next_label

    # Return function and hook
    return train_inputs, iterator_initializer_hook


def get_test_inputs(batch_size, mnist_data):
    """Return the input function to get the test data.

    Args:
        batch_size (int): Batch size of training iterator that is returned
                          by the input function.
        mnist_data (Object): Object holding the loaded mnist data.

    Returns:
        (Input function, IteratorInitializerHook):
            - Function that returns (features, labels) when called.
            - Hook to initialise input iterator.
    """
    iterator_initializer_hook = IteratorInitializerHook()

    def test_inputs():
        """Returns training set as Operations.

        Returns:
            (features, labels) Operations that iterate over the dataset
            on every evaluation
        """
        with tf.name_scope('Test_data'):
            # Get Mnist data
            images = mnist_data.test.images.reshape([-1, 28, 28, 1])
            labels = mnist_data.test.labels
            # Define placeholders
            images_placeholder = tf.placeholder(
                images.dtype, images.shape)
            labels_placeholder = tf.placeholder(
                labels.dtype, labels.shape)
            # Build dataset iterator
            dataset = tf.contrib.data.Dataset.from_tensor_slices(
                (images_placeholder, labels_placeholder))
            dataset = dataset.batch(batch_size)
            iterator = dataset.make_initializable_iterator()
            next_example, next_label = iterator.get_next()
            # Set runhook to initialize iterator
            iterator_initializer_hook.iterator_initializer_func = \
                lambda sess: sess.run(
                    iterator.initializer,
                    feed_dict={images_placeholder: images,
                               labels_placeholder: labels})
            return next_example, next_label

    # Return function and hook
    return test_inputs, iterator_initializer_hook


# Run script ##############################################
if __name__ == "__main__":
    tf.app.run(
        main=run_experiment
    )
