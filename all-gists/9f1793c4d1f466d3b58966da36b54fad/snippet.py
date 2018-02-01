#!/usr/bin/env python

import gym
import gym.envs
import numpy as np

gym.envs.register(id='NChainCustom-v0',
                  entry_point='gym.envs.toy_text:NChainEnv',
                  kwargs={'large':100},
                  timestep_limit=200)
env = gym.make('NChainCustom-v0')

num_episodes = 10000
max_timestep = 200

agent_random = lambda ob: env.action_space.sample()
agent_oracle = lambda ob: 0
agent_coward = lambda ob: 1

def run_agent(agent, name):
    R = np.zeros((num_episodes, max_timestep))
    for ep in xrange(num_episodes):
        ob = env.reset()
        for i in xrange(max_timestep):
            assert env.observation_space.contains(ob)
            a = agent(ob)
            assert env.action_space.contains(a)
            (ob, reward, _, _) = env.step(a)
            R[ep][i] = reward
    print 'agent {} mean {} std {}'.format(name, np.mean(R), np.std(R))
                                                            
run_agent(agent_random, 'random')
run_agent(agent_oracle, 'oracle')
run_agent(agent_coward, 'coward')