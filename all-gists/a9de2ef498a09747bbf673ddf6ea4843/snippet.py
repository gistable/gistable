""" Some description.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import json
import tqdm

import numpy as np
import tensorflow as tf
import edward as ed

N_FEATURES = 2
DATA_LENGTH = 3

REAL_WEIGHT = 0.7
REAL_BIAS = 2.5
REAL_DATA = np.array([2., 4., 6.])
REAL_LABELS = REAL_WEIGHT * REAL_DATA + REAL_BIAS

MC_SAMPLES = 100


def create_fake_data():
    data = np.random.randint(0, 10, DATA_LENGTH).astype(np.float32)
    noise = np.random.randn(DATA_LENGTH).astype(np.float32)
    labels = REAL_WEIGHT * data + REAL_BIAS + noise
    return data, labels


class Model:
    def __init__(self, model_name, dropout_keep_prob=1.0):
        self.model_name = model_name
        self.dropout_keep_prob = dropout_keep_prob

        self.x = tf.placeholder(tf.float32, (DATA_LENGTH, ))
        self.y = tf.placeholder(tf.float32, (DATA_LENGTH, ))

        if self.model_name == "simple_linear":
            # -- set parameters
            self.bias = tf.get_variable("bias", [1])
            self.weight = tf.get_variable("weight", [1])  # should be 1.

            # -- set dropout (optional)
            self.add_dropout()

            # -- set model
            self.nn = self.weight * self.x + self.bias

            # -- set loss
            self.loss = tf.reduce_mean((self.y - self.nn) ** 2)

        elif self.model_name == "bayesian_simple_linear":
            # -- set priors
            self.weight_mu = tf.zeros(1)  # tf.get_variable("weight_mu", [1])  
            self.weight_sigma = tf.ones(1)  # fixed hyperparameters
            self.weight = ed.models.Normal(mu=self.weight_mu, sigma=self.weight_sigma)

            self.bias_mu = tf.zeros(1)  # tf.get_variable("bias_mu", [1])  
            self.bias_sigma = tf.ones(1)  # fixed hyperparameters
            self.bias = ed.models.Normal(mu=self.bias_mu, sigma=self.bias_sigma)

            # -- set model
            self.nn_mean = self.weight * self.x + self.bias
            self.nn_sigma = tf.ones(1)  # fixed hyperparameters
            self.nn = ed.models.Normal(mu=self.nn_mean, sigma=self.nn_sigma)

            # -- set variational parameters
            self.qweight = ed.models.Normal(
                mu=tf.get_variable("qweight_mu", initializer=tf.random_normal([1])),
                sigma=tf.nn.softplus(tf.get_variable("qweight_sigma", initializer=tf.random_normal([1]))))

            self.qbias = ed.models.Normal(
                mu=tf.get_variable("qbias_mu", initializer=tf.random_normal([1])),
                sigma=tf.nn.softplus(tf.get_variable("qbias_sigma", initializer=tf.random_normal([1]))))

            # -- inference
            self.latent_vars = {self.weight: self.qweight, self.bias: self.qbias}
            self.data = {self.nn: self.y}

            self.loss = (self.latent_vars, self.data)

        else:
            raise ValueError("Wrong model error.")

    def add_dropout(self):
        self._keep_prob = tf.Variable(name="keep_prob", initial_value=self.dropout_keep_prob, trainable=False)

        self.bias = tf.cond(
            self._keep_prob < 1.0, lambda: tf.nn.dropout(self.bias, keep_prob=self._keep_prob), lambda: self.bias)
        self.weight = tf.cond(
            self._keep_prob < 1.0, lambda: tf.nn.dropout(self.weight, keep_prob=self._keep_prob), lambda: self.weight)

    @property
    def keep_prob(self):
        return self._keep_prob

    def optimize(self):

        if _is_loss_function(self.loss):
            # loss optimization
            self.optimizer = tf.train.GradientDescentOptimizer(.005)
            self.train_op = self.optimizer.minimize(self.loss)

        else:
            # variational inference
            latent_vars, data = self.loss
            self.inference = ed.KLqp(latent_vars=latent_vars, data=data)
            self.inference.initialize()
            self.train_op = self.inference

        return self.train_op


def _is_loss_function(loss):
    return isinstance(loss, tf.Tensor)


def _section(text):
    print("-"*10 + " ", text.upper())


def _tau_inv(keep_prob, N, l2=0.005, lambda_=0.00001):
    # -- Variational Dropout Uncertainty Interval by Gal
    # https://github.com/yaringal/DropoutUncertaintyDemos/blob/master/convnetjs/regression_uncertainty.js
    tau = keep_prob * l2 / (2. * N * lambda_)
    return 1. / tau


def main(model_name, dropout_keep_prob=1.0):
    _section("set model")
    model = Model(model_name, dropout_keep_prob)
    train_op = model.optimize()

    local_init_op = tf.local_variables_initializer()
    global_init_op = tf.global_variables_initializer()

    tvars = tf.trainable_variables()

    _section("train")
    with tf.Session() as sess:
        sess.run([local_init_op, global_init_op])

        tq = tqdm.trange(2000)
        for it in tq:
            data, labels = create_fake_data()

            if _is_loss_function(model.loss):
                sess.run(train_op, feed_dict={
                    model.x: data,
                    model.y: labels,
                })
                weight_, bias_ = sess.run([model.weight, model.bias])
                tq.set_postfix(weight=weight_, bias=bias_)

            else:
                train_op.update(feed_dict={
                    model.x: data, 
                    model.y: labels,
                })
                weight_, bias_ = sess.run([model.weight.value(), model.bias.value()])
                tq.set_postfix(weight=weight_, bias=bias_)

        print("trainable variables:", json.dumps({t.name: sess.run(t).tolist() for t in tvars}, indent=4))

        _section("predict on sample data")
        print("real weight", REAL_WEIGHT)
        print("real bias", REAL_BIAS)
        print("real data", REAL_DATA)
        print("real labels", REAL_LABELS)

        # -- checking out the variable distribution
        if _is_loss_function(model.loss):
            if dropout_keep_prob < 1.0:
                # don't do dropout for point estimate
                sess.run(model.keep_prob.assign(1.0))
                _section("loss optimization w/ dropout")
            else:
                _section("loss optimization")

            nn_point_estimate, weight_point_estimate, bias_point_estimate = \
                sess.run([model.nn, model.weight, model.bias], feed_dict={
                    model.x: REAL_DATA, 
                    model.y: REAL_LABELS,
                })
            print("weight point estimate", weight_point_estimate)
            print("bias point estimate", bias_point_estimate)
            print("nn point estimate", nn_point_estimate)
            print("mean absolute error", np.mean(np.absolute(nn_point_estimate - REAL_LABELS)))

            if dropout_keep_prob < 1.0:
                _section("monte carlo simulations")

                sess.run(model.keep_prob.assign(dropout_keep_prob))

                nn_mc = []
                for _ in range(MC_SAMPLES):
                    nn_mc.append(sess.run([model.nn], feed_dict={model.x: REAL_DATA, model.y: REAL_LABELS}))
                nn_mc = np.array(nn_mc)

                print("monte carlo nn mean", np.mean(nn_mc, axis=0))
                print("monte carlo nn variance", np.var(nn_mc, axis=0))
                print("+ Gal inverse precision", np.var(nn_mc, axis=0) + _tau_inv(dropout_keep_prob, MC_SAMPLES))
                print("mean absolute error", np.mean(np.absolute(np.mean(nn_mc, axis=0) - REAL_LABELS)))

        else:
            _section("variational inference")

            weight_mean, weight_var = sess.run(tf.nn.moments(model.qweight.sample(MC_SAMPLES), axes=[0]))
            print("weight posterior mean and variance", weight_mean, weight_var)
            bias_mean, bias_var = sess.run(tf.nn.moments(model.qbias.sample(MC_SAMPLES), axes=[0]))
            print("bias posterior mean and variance", bias_mean, bias_var)

            _section("prior predictive checks")
            prior = ed.copy(model.nn, {
                model.weight: model.weight.mean(), model.bias: model.bias.mean(),
            }, scope="copied/prior")

            nn_prior = []
            for _ in range(MC_SAMPLES):
                nn_prior.append(sess.run(prior.value(), feed_dict={model.x: REAL_DATA, model.y: REAL_LABELS}))
            nn_prior = np.array(nn_prior)

            print("nn prior mean and variance", np.mean(nn_prior, axis=0), np.var(nn_prior, axis=0))
            print("mean absolute error", np.mean(np.absolute(np.mean(nn_prior, axis=0) - REAL_LABELS)))

            _section("posterior predictive checks")
            posterior = ed.copy(model.nn, dict_swap={
                model.weight: model.qweight.mean(), model.bias: model.qbias.mean(),
            }, scope="copied/posterior")

            nn_post = sess.run(posterior.sample(MC_SAMPLES), feed_dict={model.x: REAL_DATA})

            print("nn posterior mean and variance", np.mean(nn_post, axis=0), np.var(nn_post, axis=0))
            print("mean absolute error", np.mean(np.absolute(np.mean(nn_post, axis=0) - REAL_LABELS)))


    # TODO: plot?


if __name__ == '__main__':
    """ Try the following:

    >>> python tf_vi_tutorial.py simple_linear
    >>> python tf_vi_tutorial.py simple_linear .9
    >>> python tf_vi_tutorial.py bayesian_simple_linear
    """
    args = sys.argv

    if len(args) == 1:
        main("simple_linear")
    elif len(args) == 2:
        _, model_name = args
        main(model_name)
    elif len(args) == 3:
        _, model_name, dropout_keep_prob = args
        dropout_keep_prob = float(dropout_keep_prob)
        assert 0 < dropout_keep_prob <= 1.0, "keep it real"
        main(model_name, float(dropout_keep_prob))
