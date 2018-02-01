#!/usr/bin/env python

import gym
import numpy as np
import tensorflow as tf


class PolicyGradientAgent(object):

    def __init__(self, hparams, sess):

        # initialization
        self._s = sess

        # build the graph
        self._input = tf.placeholder(tf.float32,
                shape=[None, hparams['input_size']])

        hidden1 = tf.contrib.layers.fully_connected(
                inputs=self._input,
                num_outputs=hparams['hidden_size'],
                activation_fn=tf.nn.relu,
                weights_initializer=tf.random_normal)

        logits = tf.contrib.layers.fully_connected(
                inputs=hidden1,
                num_outputs=hparams['num_actions'],
                activation_fn=None)

        # op to sample an action
        self._sample = tf.reshape(tf.multinomial(logits, 1), [])

        # get log probabilities
        log_prob = tf.log(tf.nn.softmax(logits))

        # training part of graph
        self._acts = tf.placeholder(tf.int32)
        self._advantages = tf.placeholder(tf.float32)

        # get log probs of actions from episode
        indices = tf.range(0, tf.shape(log_prob)[0]) * tf.shape(log_prob)[1] + self._acts
        act_prob = tf.gather(tf.reshape(log_prob, [-1]), indices)

        # surrogate loss
        loss = -tf.reduce_sum(tf.mul(act_prob, self._advantages))

        # update
        optimizer = tf.train.RMSPropOptimizer(hparams['learning_rate'])
        self._train = optimizer.minimize(loss)

    def act(self, observation):
        # get one action, by sampling
        return self._s.run(self._sample, feed_dict={self._input: [observation]})

    def train_step(self, obs, acts, advantages):
        batch_feed = { self._input: obs, \
                self._acts: acts, \
                self._advantages: advantages }
        self._s.run(self._train, feed_dict=batch_feed)


def policy_rollout(env, agent):
    """Run one episode."""

    observation, reward, done = env.reset(), 0, False
    obs, acts, rews = [], [], []

    while not done:

        env.render()
        obs.append(observation)

        action = agent.act(observation)
        observation, reward, done, _ = env.step(action)

        acts.append(action)
        rews.append(reward)

    return obs, acts, rews


def process_rewards(rews):
    """Rewards -> Advantages for one episode. """

    # total reward: length of episode
    return [len(rews)] * len(rews)


def main():

    env = gym.make('CartPole-v0')

    monitor_dir = '/tmp/cartpole_exp1'
    env.monitor.start(monitor_dir, force=True)

    # hyper parameters
    hparams = {
            'input_size': env.observation_space.shape[0],
            'hidden_size': 36,
            'num_actions': env.action_space.n,
            'learning_rate': 0.1
    }

    # environment params
    eparams = {
            'num_batches': 40,
            'ep_per_batch': 10
    }

    with tf.Graph().as_default(), tf.Session() as sess:

        agent = PolicyGradientAgent(hparams, sess)

        sess.run(tf.initialize_all_variables())

        for batch in xrange(eparams['num_batches']):

            print '=====\nBATCH {}\n===='.format(batch)

            b_obs, b_acts, b_rews = [], [], []

            for _ in xrange(eparams['ep_per_batch']):

                obs, acts, rews = policy_rollout(env, agent)

                print 'Episode steps: {}'.format(len(obs))

                b_obs.extend(obs)
                b_acts.extend(acts)

                advantages = process_rewards(rews)
                b_rews.extend(advantages)

            # update policy
            # normalize rewards; don't divide by 0
            b_rews = (b_rews - np.mean(b_rews)) / (np.std(b_rews) + 1e-10)

            agent.train_step(b_obs, b_acts, b_rews)

        env.monitor.close()


if __name__ == "__main__":
    main()