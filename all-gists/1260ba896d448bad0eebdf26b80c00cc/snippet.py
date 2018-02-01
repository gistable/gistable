import gym
import random

import numpy as np
import tensorflow as tf

class DQN:
  REPLAY_MEMORY_SIZE = 10000
  RANDOM_ACTION_PROB = 0.5
  RANDOM_ACTION_DECAY = 0.99
  HIDDEN1_SIZE = 128
  HIDDEN2_SIZE = 128
  NUM_EPISODES = 3000
  MAX_STEPS = 1000
  LEARNING_RATE = 0.0001
  MINIBATCH_SIZE = 10
  DISCOUNT_FACTOR = 0.9
  TARGET_UPDATE_FREQ = 100
  REG_FACTOR = 0.001
  LOG_DIR = '/tmp/dqn'

  def __init__(self, env):
    self.env = gym.make(env)
    assert len(self.env.observation_space.shape) == 1
    self.input_size = self.env.observation_space.shape[0]
    self.output_size = self.env.action_space.n
    
  def init_network(self):
    # Inference
    self.x = tf.placeholder(tf.float32, [None, self.input_size])
    with tf.name_scope('hidden1'):
      W1 = tf.Variable(
                 tf.truncated_normal([self.input_size, self.HIDDEN1_SIZE], 
                 stddev=0.01), name='W1')
      b1 = tf.Variable(tf.zeros(self.HIDDEN1_SIZE), name='b1')
      h1 = tf.nn.tanh(tf.matmul(self.x, W1) + b1)
    with tf.name_scope('hidden2'):
      W2 = tf.Variable(
                 tf.truncated_normal([self.HIDDEN1_SIZE, self.HIDDEN2_SIZE], 
                 stddev=0.01), name='W2')
      b2 = tf.Variable(tf.zeros(self.HIDDEN2_SIZE), name='b2')
      h2 = tf.nn.tanh(tf.matmul(h1, W2) + b2)
    with tf.name_scope('output'):
      W3 = tf.Variable(
                 tf.truncated_normal([self.HIDDEN2_SIZE, self.output_size], 
                 stddev=0.01), name='W3')
      b3 = tf.Variable(tf.zeros(self.output_size), name='b3')
      self.Q = tf.matmul(h2, W3) + b3
    self.weights = [W1, b1, W2, b2, W3, b3]

    # Loss
    self.targetQ = tf.placeholder(tf.float32, [None])
    self.targetActionMask = tf.placeholder(tf.float32, [None, self.output_size])
    # TODO: Optimize this
    q_values = tf.reduce_sum(tf.mul(self.Q, self.targetActionMask), 
                  reduction_indices=[1])
    self.loss = tf.reduce_mean(tf.square(tf.sub(q_values, self.targetQ)))

    # Reguralization
    for w in [W1, W2, W3]:
      self.loss += self.REG_FACTOR * tf.reduce_sum(tf.square(w))

    # Training
    optimizer = tf.train.GradientDescentOptimizer(self.LEARNING_RATE)
    global_step = tf.Variable(0, name='global_step', trainable=False)
    self.train_op = optimizer.minimize(self.loss, global_step=global_step)

  def train(self, num_episodes=NUM_EPISODES):
    replay_memory = []

    self.session = tf.Session()

    # Summary for TensorBoard
    tf.scalar_summary('loss', self.loss)
    self.summary = tf.merge_all_summaries()
    self.summary_writer = tf.train.SummaryWriter(self.LOG_DIR, self.session.graph)

    self.session.run(tf.initialize_all_variables())
    total_steps = 0

    for episode in range(num_episodes):
      print("Training: Episode = %d, Global step = %d" % (episode, total_steps))
      state = self.env.reset()
      target_weights = self.session.run(self.weights)

      for step in range(self.MAX_STEPS):
        # Pick the next action and execute it
        action = None
        if random.random() < self.RANDOM_ACTION_PROB:
          action = self.env.action_space.sample()
        else:
          q_values = self.session.run(self.Q, feed_dict={self.x: [state]})
          action = q_values.argmax()
        self.RANDOM_ACTION_PROB *= self.RANDOM_ACTION_DECAY
        obs, reward, done, _ = self.env.step(action)

        # Update replay memory
        if done:
          reward = -100
        replay_memory.append((state, action, reward, obs, done))
        if len(replay_memory) > self.REPLAY_MEMORY_SIZE:
          replay_memory.pop(0)
        state = obs

        # Sample a random minibatch and fetch max Q at s'
        if len(replay_memory) >= self.MINIBATCH_SIZE:
          minibatch = random.sample(replay_memory, self.MINIBATCH_SIZE)
          next_states = [m[3] for m in minibatch]
          # TODO: Optimize to skip terminal states
          feed_dict = {self.x: next_states}
          feed_dict.update(zip(self.weights, target_weights))
          q_values = self.session.run(self.Q, feed_dict=feed_dict)
          max_q_values = q_values.max(axis=1)

          # Compute target Q values
          target_q = np.zeros(self.MINIBATCH_SIZE)
          target_action_mask = np.zeros((self.MINIBATCH_SIZE, self.output_size), dtype=int)
          for i in range(self.MINIBATCH_SIZE):
            _, action, reward, _, terminal = minibatch[i]
            target_q[i] = reward
            if not terminal:
              target_q[i] += self.DISCOUNT_FACTOR * max_q_values[i]
            target_action_mask[i][action] = 1

          # Gradient descent
          states = [m[0] for m in minibatch]
          feed_dict = {
            self.x: states, 
            self.targetQ: target_q,
            self.targetActionMask: target_action_mask,
          }
          _, summary = self.session.run([self.train_op, self.summary], 
                                        feed_dict=feed_dict)

          # Write summary for TensorBoard
          if total_steps % 100 == 0:
            self.summary_writer.add_summary(summary, total_steps)

          # Update target weights
          if total_steps % self.TARGET_UPDATE_FREQ == 0:
            target_weights = self.session.run(self.weights)

        total_steps += 1
        if done:
          break

  def play(self):
    state = self.env.reset()
    done = False
    steps = 0
    while not done and steps < 200:
      self.env.render()
      q_values = self.session.run(self.Q, feed_dict={self.x: [state]})
      action = q_values.argmax()
      state, _, done, _ = self.env.step(action)
      steps += 1
    return steps

if __name__ == '__main__':
  dqn = DQN('CartPole-v0')
  dqn.init_network()

  dqn.env.monitor.start('/tmp/cartpole')
  dqn.train()
  dqn.env.monitor.close()

  res = []
  for i in range(100):
    steps = dqn.play()
    print("Test steps = ", steps)
    res.append(steps)
  print("Mean steps = ", sum(res) / len(res))
