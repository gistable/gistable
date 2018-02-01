# From udacity Machine Learning Nanodegree course

import numpy as np

# Define sigmoid function
def sigmoid(x):
  return 1/(1+np.exp(-x))

# Derivative of the sigmoid function
def sigmoid_derivative(x):
  return sigmoid(x) * (1 - sigmoid(x))

# Feature data
feature = np.array([0.9, -0.2])

# Label data (Target)
label = 0.9

# Weights of neural network
weights = np.array([0.3, -0.8])

# The learning rate, eta in the weight step equation
learnrate = 0.1

# the linear combination performed by the node (h in f(h) and f'(h))
h = np.dot(feature, weights)

# The neural network output (label-hat)
nn_output = sigmoid(h)

# output error (label - label-hat)
error = label - nn_output

# output gradient (f'(h))
output_grad = sigmoid_derivative(h)

# error term (lowercase delta)
error_term = error * output_grad

# Gradient descent step 
del_w = learnrate * error_term * feature

print('Output: %s' % nn_output)
print('Error: %s' % error)
print('Change in Weights: %s' % del_w)
