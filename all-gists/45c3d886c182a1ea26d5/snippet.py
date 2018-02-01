import numpy as np
import tensorflow as tf
from scipy.optimize import minimize
import matplotlib
matplotlib.use('PDF')
import matplotlib.pyplot as plt

# Generate dataset
data = np.random.normal(0, 1, 1000)

sess = tf.Session()

# Lots of casting here, unfortunately
X = tf.Variable(data)
mu = tf.Variable(np.float64(1))
sigma = tf.Variable(np.float64(1))

# Define negative log-likelihood and gradient
def normal_log(X, mu, sigma, left=-np.inf, right=np.inf):
    val = -tf.log(tf.constant(np.sqrt(2 * np.pi), dtype=tf.float64) * sigma) - \
           tf.pow(X - mu, 2) / (tf.constant(2, dtype=tf.float64) * tf.pow(sigma, 2))
    return val

nll = -tf.reduce_sum(normal_log(X, mu, sigma))
grad = tf.gradients(nll, [mu, sigma])

def objective(params):
    mu_, sigma_ = params
    return sess.run(nll, feed_dict={ mu: mu_, sigma: sigma_ })

def gradient(params):
    mu_, sigma_ = params
    ret =  sess.run(grad, feed_dict={ mu: mu_, sigma: sigma_ })
    return np.array(ret)

# Variables need to be initialized
init = tf.initialize_all_variables()
sess.run(init)

# Find optimum
ret = minimize(objective, x0=np.array([5, 5]), jac=gradient)
params = ret['x']

# Plot results
plt.hist(data, bins=20, histtype='step', color='k', normed=True)
xs = np.linspace(-5, 5, 200)
plt.plot(xs, sess.run(tf.exp(normal_log(xs, *params))))
plt.savefig('out.pdf')