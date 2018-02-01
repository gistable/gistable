#%% (0) Important libraries
import tensorflow as tf
import numpy as np
from numpy import random
import matplotlib.pyplot as plt
from IPython import display
% matplotlib inline

#%% (1) Dataset creation.

def as_bytes(num, final_size):
    """Converts an integer to a reversed bitstring (of size final_size).
    
    Arguments
    ---------
    num: int
        The number to convert.
    final_size: int
        The length of the bitstring.
        
    Returns
    -------
    list:
        A list which is the reversed bitstring representation of the given number.
        
    Examples
    --------
    >>> as_bytes(3, 4)
    [1, 1, 0, 0]
    >>> as_bytes(3, 5)
    [1, 1, 0, 0, 0]
    """
    res = []
    for _ in range(final_size):
        res.append(num % 2)
        num //= 2
    return res

def generate_example(num_bits):
    """Generate an example addition.
    
    Arguments
    ---------
    num_bits: int
        The number of bits to use.
        
    Returns
    -------
    a: list
        The first term (represented as reversed bitstring) of the addition.
    b: list
        The second term (represented as reversed bitstring) of the addition.
    c: list
        The addition (a + b) represented as reversed bitstring.
        
    Examples
    --------
    >>> np.random.seed(4)
    >>> a, b, c = generate_example(3)
    >>> a
    [0, 1, 0]
    >>> b
    [0, 1, 0]
    >>> c
    [1, 0, 0]
    >>> # Notice that these numbers are represented as reversed bitstrings)
    """
    a = random.randint(0, 2**(num_bits - 1) - 1)
    b = random.randint(0, 2**(num_bits - 1) - 1)
    res = a + b
    return (as_bytes(a,  num_bits),
            as_bytes(b,  num_bits),
            as_bytes(res,num_bits))

def generate_batch(num_bits, batch_size):
    """Generates instances of the addition problem.
    
    Arguments
    ---------
    num_bits: int
        The number of bits to use for each number.
    batch_size: int
        The number of examples to generate.
    
    Returns
    -------
    x: np.array
        Two numbers to be added represented as bits (in reversed order).
        Shape: b, i, n
        Where:
            b is bit index from the end.
            i is example idx in batch.
            n is one of [0,1] depending for first and second summand respectively.
    y: np.array
        The result of the addition.
        Shape: b, i, n
        Where:
            b is bit index from the end.
            i is example idx in batch.
            n is always 0 since there is only one result.
    """
    x = np.empty((batch_size, num_bits, 2))
    y = np.empty((batch_size, num_bits, 1))

    for i in range(batch_size):
        a, b, r = generate_example(num_bits)
        x[i, :, 0] = a
        x[i, :, 1] = b
        y[i, :, 0] = r
    return x, y

# Configuration
batch_size = 100
time_size = 5

# Generate a test set and a train set containing 100 examples of numbers represented in 5 bits
X_train, Y_train = generate_batch(time_size, batch_size)
X_test, Y_test = generate_batch(time_size, batch_size)

#%% (2) Model definition.

import tensorflow as tf

class GRU:
    """Implementation of a Gated Recurrent Unit (GRU) as described in [1].
    
    [1] Chung, J., Gulcehre, C., Cho, K., & Bengio, Y. (2014). Empirical evaluation of gated recurrent neural networks on sequence modeling. arXiv preprint arXiv:1412.3555.
    
    Arguments
    ---------
    input_dimensions: int
        The size of the input vectors (x_t).
    hidden_size: int
        The size of the hidden layer vectors (h_t).
    dtype: obj
        The datatype used for the variables and constants (optional).
    """
    
    def __init__(self, input_dimensions, hidden_size, dtype=tf.float64):
        self.input_dimensions = input_dimensions
        self.hidden_size = hidden_size
        
        # Weights for input vectors of shape (input_dimensions, hidden_size)
        self.Wr = tf.Variable(tf.truncated_normal(dtype=dtype, shape=(self.input_dimensions, self.hidden_size), mean=0, stddev=0.01), name='Wr')
        self.Wz = tf.Variable(tf.truncated_normal(dtype=dtype, shape=(self.input_dimensions, self.hidden_size), mean=0, stddev=0.01), name='Wz')
        self.Wh = tf.Variable(tf.truncated_normal(dtype=dtype, shape=(self.input_dimensions, self.hidden_size), mean=0, stddev=0.01), name='Wh')
        
        # Weights for hidden vectors of shape (hidden_size, hidden_size)
        self.Ur = tf.Variable(tf.truncated_normal(dtype=dtype, shape=(self.hidden_size, self.hidden_size), mean=0, stddev=0.01), name='Ur')
        self.Uz = tf.Variable(tf.truncated_normal(dtype=dtype, shape=(self.hidden_size, self.hidden_size), mean=0, stddev=0.01), name='Uz')
        self.Uh = tf.Variable(tf.truncated_normal(dtype=dtype, shape=(self.hidden_size, self.hidden_size), mean=0, stddev=0.01), name='Uh')
        
        # Biases for hidden vectors of shape (hidden_size,)
        self.br = tf.Variable(tf.truncated_normal(dtype=dtype, shape=(self.hidden_size,), mean=0, stddev=0.01), name='br')
        self.bz = tf.Variable(tf.truncated_normal(dtype=dtype, shape=(self.hidden_size,), mean=0, stddev=0.01), name='bz')
        self.bh = tf.Variable(tf.truncated_normal(dtype=dtype, shape=(self.hidden_size,), mean=0, stddev=0.01), name='bh')
        
        # Define the input layer placeholder
        self.input_layer = tf.placeholder(dtype=tf.float64, shape=(None, None, input_dimensions), name='input')
        
        # Put the time-dimension upfront for the scan operator
        self.x_t = tf.transpose(self.input_layer, [1, 0, 2], name='x_t')
        
        # A little hack (to obtain the same shape as the input matrix) to define the initial hidden state h_0
        self.h_0 = tf.matmul(self.x_t[0, :, :], tf.zeros(dtype=tf.float64, shape=(input_dimensions, hidden_size)), name='h_0')
        
        # Perform the scan operator
        self.h_t_transposed = tf.scan(self.forward_pass, self.x_t, initializer=self.h_0, name='h_t_transposed')
        
        # Transpose the result back
        self.h_t = tf.transpose(self.h_t_transposed, [1, 0, 2], name='h_t')

    def forward_pass(self, h_tm1, x_t):
        """Perform a forward pass.
        
        Arguments
        ---------
        h_tm1: np.matrix
            The hidden state at the previous timestep (h_{t-1}).
        x_t: np.matrix
            The input vector.
        """
        # Definitions of z_t and r_t
        z_t = tf.sigmoid(tf.matmul(x_t, self.Wz) + tf.matmul(h_tm1, self.Uz) + self.bz)
        r_t = tf.sigmoid(tf.matmul(x_t, self.Wr) + tf.matmul(h_tm1, self.Ur) + self.br)
        
        # Definition of h~_t
        h_proposal = tf.tanh(tf.matmul(x_t, self.Wh) + tf.matmul(tf.multiply(r_t, h_tm1), self.Uh) + self.bh)
        
        # Compute the next hidden state
        h_t = tf.multiply(1 - z_t, h_tm1) + tf.multiply(z_t, h_proposal)
        
        return h_t
    
#%% (3) Initialize and train the model.

# The input has 2 dimensions: dimension 0 is reserved for the first term and dimension 1 is reverved for the second term
input_dimensions = 2

# Arbitrary number for the size of the hidden state
hidden_size = 16

# Initialize a session
session = tf.Session()

# Create a new instance of the GRU model
gru = GRU(input_dimensions, hidden_size)

# Add an additional layer on top of each of the hidden state outputs
W_output = tf.Variable(tf.truncated_normal(dtype=tf.float64, shape=(hidden_size, 1), mean=0, stddev=0.01))
b_output = tf.Variable(tf.truncated_normal(dtype=tf.float64, shape=(1,), mean=0, stddev=0.01))
output = tf.map_fn(lambda h_t: tf.matmul(h_t, W_output) + b_output, gru.h_t)

# Create a placeholder for the expected output
expected_output = tf.placeholder(dtype=tf.float64, shape=(batch_size, time_size, 1), name='expected_output')

# Just use quadratic loss
loss = tf.reduce_sum(0.5 * tf.pow(output - expected_output, 2)) / float(batch_size)

# Use the Adam optimizer for training
train_step = tf.train.AdamOptimizer().minimize(loss)

# Initialize all the variables
init_variables = tf.global_variables_initializer()
session.run(init_variables)

# Initialize the losses
train_losses = []
validation_losses = []

# Perform all the iterations
for epoch in range(5000):
    # Compute the losses
    _, train_loss = session.run([train_step, loss], feed_dict={gru.input_layer: X_train, expected_output: Y_train})
    validation_loss = session.run(loss, feed_dict={gru.input_layer: X_test, expected_output: Y_test})
    
    # Log the losses
    train_losses += [train_loss]
    validation_losses += [validation_loss]
    
    # Display an update every 50 iterations
    if epoch % 50 == 0:
        plt.plot(train_losses, '-b', label='Train loss')
        plt.plot(validation_losses, '-r', label='Validation loss')
        plt.legend(loc=0)
        plt.title('Loss')
        plt.xlabel('Iteration')
        plt.ylabel('Loss')
        plt.show()
        print('Iteration: %d, train loss: %.4f, test loss: %.4f' % (epoch, train_loss, validation_loss))
    
#%% (4) Manually evaluate the model.
    
# Define two numbers a and b and let the model compute a + b
a = 1024
b = 16

# The model is independent of the sequence length! Now we can test the model on even longer bitstrings
bitstring_length = 20

# Create the feature vectors    
X_custom_sample = np.vstack([as_bytes(a, bitstring_length), as_bytes(b, bitstring_length)]).T
X_custom = np.zeros((1,) + X_custom_sample.shape)
X_custom[0, :, :] = X_custom_sample

# Make a prediction by using the model
y_predicted = session.run(output, feed_dict={gru.input_layer: X_custom})
# Just use a linear class separator at 0.5
y_bits = 1 * (y_predicted > 0.5)[0, :, 0]
# Join and reverse the bitstring
y_bitstr = ''.join([str(int(bit)) for bit in y_bits.tolist()])[::-1]
# Convert the found bitstring to a number
y = int(y_bitstr, 2)

# Print out the prediction
print(y) # Yay! This should equal 1024 + 16 = 1040