#!/usr/bin/env python

## NAME
## Neural Network from scratch
##
## DESCRIPTION
## A partially-refactored, variable-name-expanded, heavily commented version
## of Denny Britz's code. Original blog post:
## http://www.wildml.com/2015/09/implementing-a-neural-network-from-scratch/
##
## Designed for maximum readibility and concept comprehension. Output
## is a scatterplot image (png format.)
##
## AUTHOR
## Spencer Hoffman <spencer.hoffman@gmail.com>
##
##

import matplotlib
import matplotlib.pyplot as plotter
import numpy as np
import sklearn
import sklearn.datasets
import sklearn.linear_model

def main():
  ## The dimensionality of the layers.
  layer_dimensions = {
    'input': 2,
    'output': 2,
    'hidden': 3
  }

  ## Distance between points in the output.
  POINT_DISTANCE = 0.01

  ## Padding for the output graphs
  ADJUSTMENT_VAL = 0.5

  ## Gradient descent params
  LEARNING_RATE = 0.01
  REGULARIZATION_STRENGTH = 0.01
  NUM_PASSES = 20000

  np.random.seed(0)

  ## Get some training data.
  samples, labels = sklearn.datasets.make_moons(200, noise=0.20)

  ## Training set size
  num_examples = (len(samples))

  plotter.scatter(
    samples[:,0],
    samples[:,1],
    s=40,
    c=labels,
   cmap=plotter.cm.Spectral
  )

  logistic_regression_classifier = sklearn.linear_model.LogisticRegressionCV()

  logistic_regression_classifier.fit(samples, labels)
  plot_decision_boundary(
    lambda x: logistic_regression_classifier.predict(x),
    samples,
    labels,
    ADJUSTMENT_VAL,
    POINT_DISTANCE
 )

  plotter.savefig('logistic_regression.png')

  model = build_model(
    layer_dimensions,
    num_examples,
    samples,
    labels,
    REGULARIZATION_STRENGTH,
    LEARNING_RATE,
    NUM_PASSES=NUM_PASSES,
    show_loss=True
  )

  plot_decision_boundary(
    lambda x: predict(model, x),
    samples,
    labels,
    ADJUSTMENT_VAL,
    POINT_DISTANCE
  )

  plotter.savefig('final_plot.png')

def calculate_loss(model, samples, labels, num_examples, STRENGTH):
  """ Measures our network's learning error

      Args:
        model: The weights and biases for the network
        samples: Training data points
        labels: Training data class labels
        num_examples: Size of sample set
        STRENGTH: The value for regularization to prevent overfitting

      Returns:
        A floating point value representing our network learning error
  """

  probabilities, t = forward_propagate(
    model['weights'],
    model['biases'],
    samples
  )

  ## Calculate the loss using cross-entropy (AKA negative log-likelihood.)
  log_probabilities = -np.log(probabilities[range(num_examples), labels])
  data_loss = np.sum(log_probabilities)

  ## Regularize the data loss.
  data_loss += (STRENGTH / 2) * (
    np.sum(np.square(model['weights']['layer1'])) +
    np.sum(np.square(model['weights']['layer2']))
  )
  
  return 1.0 / num_examples * data_loss

def plot_decision_boundary(predictor_func, samples, labels, ADJUSTMENT_VAL,
                           distance):
  """ Sets up the plots for the output 

      Args:
        predictor_func: A function we use to get our network's predictions
        samples: Training data points
        labels: Training data class labels
        ADJUSTMENT_VAL: Tweak value for the sample and label values
        distance: Space between points in the output
  """

  ## Set min and max values with some tweaks.
  samples_min, samples_max = \
    samples[:, 0].min() - ADJUSTMENT_VAL, samples[:, 0].max() + ADJUSTMENT_VAL

  labels_min, labels_max = \
    samples[:, 1].min() - ADJUSTMENT_VAL, samples[:, 1].max() + ADJUSTMENT_VAL 

  ## Generate a grid of points with some amount of distance between them.
  sample_section, label_section = np.meshgrid(
    np.arange(samples_min, samples_max, distance),
    np.arange(labels_min, labels_max, distance)
  )

  ## Predict the function value for the whole grid.
  prediction_value = predictor_func(np.c_[
    sample_section.ravel(),
    label_section.ravel()
  ])

  ## Reshape the prediction array so it displays properly.
  prediction_value = prediction_value.reshape(sample_section.shape)

  ## Draw the decision boundary.
  plotter.contourf(
    sample_section,
    label_section,
    prediction_value,
    cmap=plotter.cm.Spectral
  )

  ## Draw the points.
  plotter.scatter(
    samples[:, 0],
    samples[:, 1], 
    c=labels,
    cmap=plotter.cm.Spectral
  )

def build_model(layer_dimensions, num_examples, samples, labels, STRENGTH,
                LEARNING_RATE, NUM_PASSES=20000, show_loss=False):
  """ Calculates weights and biases for the vectors/neurons in our network.

      Args:
        layer_dimensions: number of neurons in each layer
        num_examples: Size of sample set
        samples: Training data points
        labels: Training data class labels
        STRENGTH: The value for regularization to prevent overfitting
        LEARNING_RATE: AKA step size. Determines how quickly we allow
        the network to learn. Low values make convergence happen properly,
        but at the cost of speed. High values are faster, but can cause
        divergence.
        NUM_PASSES: How many times we loop when performing gradient descent
        show_loss: Whether or not to show the loss values during the run

      Returns:
        A dictionary with keys for weights and biases
  """

  ## Initialize params to random values. We need to learn these.
  np.random.seed(0)

  ## Weights and biases for the vectors/neurons in the hidden layers. We
  ## set them up to be random values initially.
  ## Weights describe how important a given input is to its repsective output.
  weights = {

    'layer1': np.random.randn(layer_dimensions['input'],
      layer_dimensions['hidden']) / np.sqrt(layer_dimensions['input']),

    'layer2': np.random.randn(
      layer_dimensions['hidden'],
      layer_dimensions['output']) / np.sqrt(layer_dimensions['hidden'])

  }

  ## Biases represent thresholds for activating a neuron. The higher
  ## this is, the more likely a neuron is to fire.
  biases = {

    'layer1': np.zeros((1, layer_dimensions['hidden'])),
    'layer2': np.zeros((1, layer_dimensions['output']))

  }

  ## Store the differences between our expectations, and what we've found
  ## so far. Used to improve our actual weight and bias values.
  error_deltas = {

    'weights': { 'layer1': None, 'layer2': None },
    'biases': { 'layer1': None, 'layer2': None },
    'layer2': None,
    'layer1': None
      
  }

  ## Perform backward propagation of errors using gradient descent.
  for i in xrange(0, NUM_PASSES):

    ## First, forward propagate. 
    current_probabilities, activations = forward_propagate(
      weights,
      biases,
      samples
    )

    ## Continue backpropagation of errors.
    ## We perform an assignment to make it clear that layer2 starts out
    ## as the current set of probablities, though we could just set this
    ## in the call above. We start at the uppermost hidden layer and
    ## work our way back. Now start calculating the error deltas from
    ## our hidden layers to help get our weights and biases closer to
    ## the correct values. 
    error_deltas['layer2'] = current_probabilities

    ## We subtract one from the deltas to help us determine how far off
    ## from the desired value we are. If the values are close to zero (i.e.,
    ## very small negative numbers), then we are close. If they are
    ## larger negative numbers, then we are further from said desired value.
    error_deltas['layer2'][range(num_examples), labels] -= 1

    ## The next steps are an implementation of Calculus' chain rule.
    error_deltas['weights']['layer2'] = (activations.T).dot(
      error_deltas['layer2']
    )

    error_deltas['biases']['layer2'] = np.sum(
      error_deltas['layer2'],
      axis=0,
      keepdims=True
    )

    error_deltas['layer1'] = error_deltas['layer2'].dot(
      weights['layer2'].T) * (1 - np.power(activations, 2))

    error_deltas['weights']['layer1'] = np.dot(
      samples.T,
      error_deltas['layer1']
    )

    error_deltas['biases']['layer1'] = np.sum(error_deltas['layer1'], axis=0)

    ## Regularize weights to combat overfitting. Note that using
    ## regularization combined with softmax() is effectively using
    ## Maximum a posteriori estimation (MAP)
    error_deltas['weights']['layer2'] += STRENGTH * weights['layer2']
    error_deltas['weights']['layer1'] += STRENGTH * weights['layer1']

    ## Update our weights and biases using the specified learning rate.
    weights['layer1'] += -LEARNING_RATE * error_deltas['weights']['layer1']
    biases['layer1'] += -LEARNING_RATE * error_deltas['biases']['layer1']
    weights['layer2'] += -LEARNING_RATE * error_deltas['weights']['layer2']
    biases['layer2'] += -LEARNING_RATE * error_deltas['biases']['layer2']

    if show_loss and i % 1000 == 0:
      print "Loss after iteration %i: %f" % (i,
          calculate_loss(
            {'weights': weights, 'biases': biases},
            samples,
            labels,
            num_examples,
            STRENGTH
            )
          )

  return {'weights': weights, 'biases': biases}

def predict(model, samples):
  """ Predict the highest probabilities. This is the output of the network
      Args:
        model: The weights and biases for the network
        samples: Training data points

      Returns: An ndarray of indices indicating the highest current scores.
  """

  probabilities, t = forward_propagate(
    model['weights'],
    model['biases'],
    samples
  )

  return np.argmax(probabilities, axis=1)

def softmax(products):
  """ We've already squashed the values in our products vector into the
      appropriate range (from -1 to 1, since we're using tanh() as
      our non-linearity function.) We now take these values and 
      create normalized class probabilities. Another way of thinking of
      this is that we are performing Maximum Likelihood Estimation (MLE)

      Args:
        products: Raw scores from our forward propagation step.

      Returns: A matrix of floating point numbers representing 
               normalized class probablities.
  """

  ## Exponentiation creates un-normalized products.
  exponentiated_scores = np.exp(products)

  ## Division of the sum normalizes them.
  return exponentiated_scores / np.sum(
    exponentiated_scores,
    axis=1,
    keepdims=True
  )

def forward_propagate(weights, biases, samples):
  """ Get the probabilities and activation values of our pattern's
      input through the network. Activation values are returned for
      times when we need to perform backpropagation.

      Args:
        weights: The weights for each vector in the layers
        biases: The bias values for each neuron in the layers
        samples: Training data points

      Returns:
        A list of probabilities after running through the network,
        and activations from the first hidden layer of the network.
  """

  ## Calculate our inputs. 
  layer1_products = samples.dot(weights['layer1']) + biases['layer1']

  ## Call our non-linear activation function; transforms the inputs of a
  ## layer to its outputs. This is where the neurons of the
  ## hidden layers do their work.
  layer1_activations = np.tanh(layer1_products)

  ## Now we run the output from the first hidden layer into the second
  ## hidden layer.
  layer2_products = layer1_activations.dot(weights['layer2']) + biases['layer2']

  ## Finally, we convert the raw scores (which are also activations) we
  ## receive from the second hidden layer into probabilities using softmax.
  probabilities = softmax(layer2_products)
  
  return probabilities, layer1_activations

if __name__ == '__main__':
  main()

