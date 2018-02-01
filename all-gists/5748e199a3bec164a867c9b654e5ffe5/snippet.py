import numpy as np
import gym
from gym.spaces import Discrete, Box
from gym.wrappers import Monitor
from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten


# ================================================================
# Policies
# ================================================================

class DeterministicDiscreteActionLinearPolicy(object):

    def __init__(self, theta, model, ob_space, ac_space):
        """
        dim_ob: dimension of observations
        n_actions: number of actions
        theta: flat vector of parameters
        """
        dim_ob = ob_space.shape[0]
        n_actions = ac_space.n

        #assert len(theta) == (dim_ob + 1) * n_actions
        #self.W = theta[0 : dim_ob * n_actions].reshape(dim_ob, n_actions)
        #self.b = theta[dim_ob * n_actions : None].reshape(1, n_actions)

        self.model = model

        self.shapes = [w.shape for w in self.model.get_weights()]
        self.sizes = [w.size for w in self.model.get_weights()]

        self.model.set_weights(self._get_weights_list(theta))

        self.model.compile(optimizer='sgd', loss='mse')


    def _get_weights_list(self, weights_flat):
        weights = []
        pos = 0
        for i_layer, size in enumerate(self.sizes):
            arr = weights_flat[pos:pos+size].reshape(self.shapes[i_layer])
            weights.append(arr)
            pos += size

        return weights

    def act(self, ob):
        """
        """
        batch = np.array([[ob]])
        actions = self.model.predict_on_batch(batch).flatten()
        return np.argmax(actions)

class DeterministicContinuousActionLinearPolicy(object):

    def __init__(self, theta, ob_space, ac_space):
        """
        dim_ob: dimension of observations
        dim_ac: dimension of action vector
        theta: flat vector of parameters
        """
        self.ac_space = ac_space
        dim_ob = ob_space.shape[0]
        dim_ac = ac_space.shape[0]
        assert len(theta) == (dim_ob + 1) * dim_ac
        self.W = theta[0 : dim_ob * dim_ac].reshape(dim_ob, dim_ac)
        self.b = theta[dim_ob * dim_ac : None]

    def act(self, ob):
        a = np.clip(ob.dot(self.W) + self.b, self.ac_space.low, self.ac_space.high)
        return a

def do_episode(policy, env, num_steps, discount=1.0, render=False):
    disc_total_rew = 0
    ob = env.reset()
    for t in xrange(num_steps):
        a = policy.act(ob)
        (ob, reward, done, _info) = env.step(a)
        disc_total_rew += reward * discount**t
        if render and t%3==0:
            env.render()
        if done: break
    return disc_total_rew

env = None
def noisy_evaluation(theta, discount=0.90):
    policy = make_policy(theta)
    reward = do_episode(policy, env, num_steps, discount)
    return reward

def make_policy(theta):
    if isinstance(env.action_space, Discrete):
        return DeterministicDiscreteActionLinearPolicy(theta,
            model, env.observation_space, env.action_space)
    elif isinstance(env.action_space, Box):
        return DeterministicContinuousActionLinearPolicy(theta,
            env.observation_space, env.action_space)
    else:
        raise NotImplementedError

# Task settings:
env = gym.make('CartPole-v1') # Change as needed
#env = Monitor(env, '/tmp/cartpole-experiment-1', force=True)

# Alg settings:
num_steps = 500 # maximum length of episode
n_iter = 50 # number of iterations of ES
batch_size = 25 # number of samples per batch
#extra_std = 2.0
#extra_decay_time = 10

# Model
# model = Sequential()
# model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
# model.add(Dense(env.action_space.n))
# model.add(Activation('softmax'))

model = Sequential()
model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(env.action_space.n))
model.add(Activation('softmax'))

sizes = [w.size for w in model.get_weights()]

if isinstance(env.action_space, Discrete):
    dim_theta = sum(sizes)
elif isinstance(env.action_space, Box):
    dim_theta = (env.observation_space.shape[0]+1) * env.action_space.shape[0]
else:
    raise NotImplementedError

# Initialize mean and standard deviation
epsilon_mean = np.zeros(dim_theta)
sigma = 2
epsilon_std = sigma * np.ones(dim_theta)
theta = np.random.uniform(-1, 1, size=dim_theta)
alpha = 0.001

# Now, for the algorithm
for itr in xrange(n_iter):
    # Sample parameter vectors and evaluate rewards
    #extra_cov = max(1.0 - itr / extra_decay_time, 0) * extra_std**2
    epsilons = np.random.multivariate_normal(mean=epsilon_mean,
                                           cov=np.diag(np.array(epsilon_std**2)),
                                           size=batch_size)
    rewards = np.array(map(noisy_evaluation, theta + sigma * epsilons))
    
    # standardize the rewards
    rewards = (rewards - rewards.mean()) / rewards.std()
    
    # gradient ascent with score function estimator
    theta += alpha * rewards.dot(epsilons) / (batch_size * sigma)

    print "iteration %i. mean f: %8.3g. max f: %8.3g"%(itr, np.mean(rewards), np.max(rewards))
    do_episode(make_policy(theta), env, num_steps, discount=0.90, render=True)

env.close()