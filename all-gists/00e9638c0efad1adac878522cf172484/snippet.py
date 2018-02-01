
#Evolution Strategies with Keras
#Based off of: https://blog.openai.com/evolution-strategies/
#Implementation by: Nicholas Samoray

#README
#Meant to be run on a single machine
#APPLY_BIAS is currently not working, keep to False
#Solves Cartpole as-is in about 50 episodes
#Solves BipedalWalker-v2 in about 1000
#Network used for BipedalWalker-v2
#-Input
#-128 hidden, activation tanh
#-128 hidden, activation tanh
#-Output

import gym
from keras.layers import Dense, Flatten, Input, merge, Lambda, Activation
from keras.optimizers import Adam
from keras.models import Sequential, Model
import keras.backend as K 
import tensorflow as tf
from collections import deque
import numpy as np
import random
import math
import threading
import sys

LEARN_RATE = 0.03
SIGMA = 0.1
ACTION_SIZE = 2
STATE_SIZE = 4
#total number of episodes
NUM_EPS = 10000
#number of workers
NUM_WORKERS = 64
#number of times to run each worker on the same network
NUM_TESTS = 1
#max time to run each env
EPS_LENGTH = 2000
FRAME_COUNT = 0
ENV = 'CartPole-v1'
APPLY_BIAS = False
scores = []

class network():
	def __init__(self):
		self.model = self.createModel()
		self.env = gym.make(ENV)

	def createModel(self):
		#change activations based on environment
		state_in = Input(shape=[STATE_SIZE])
		x        = Dense(24, activation='relu')(state_in)
		x        = Dense(24, activation='relu')(x)
		out      = Dense(ACTION_SIZE, activation='softmax')(x)

		model = Model(input=state_in, output=out)

		return model

	#just runs the network on the environment
	#collects reward and returns it
	def run(self):
		global FRAME_COUNT
		total_reward = 0.

		for e in range(NUM_TESTS):
			state = self.env.reset()
			state = np.reshape(state, [1, STATE_SIZE])
			for t in range(EPS_LENGTH):
				FRAME_COUNT += 1
				action = self.model.predict(state)[0]

				#comment this out if you're not doing CartPole or something
				action = np.argmax(action)

				new_state, reward, done, _ = self.env.step(action)
				total_reward += reward
				if done:
					break
				state = new_state
				state = np.reshape(state, [1, STATE_SIZE])

		return total_reward/NUM_TESTS

#progress bar methods
def startProgress(title):
    global progress_x
    sys.stdout.write(title + ": [" + "-"*40 + "]" + chr(8)*41)
    sys.stdout.flush()
    progress_x = 0

def progress(x):
    global progress_x
    x = int(x * 40 // 100)
    sys.stdout.write("#" * (x - progress_x))
    sys.stdout.flush()
    progress_x = x

def endProgress():
    sys.stdout.write("#" * (40 - progress_x) + "]\n")
    sys.stdout.flush()

#create all the workers
networks = [network() for i in range(NUM_WORKERS)]
weight_list = []

#initialize random weights
curr_weights = []
curr_bias = []
#loop through each layer in the first network to get shapes
for l in range(1,len(networks[0].model.layers)):
	#get shapes of weight and bias layers
	bias_shape = np.array(networks[0].model.layers[l].get_weights()[1]).shape
	shape = np.array(networks[0].model.layers[l].get_weights()[0]).shape

	#get the current weights of the first network as a baseline
	#init biases to 0 is we're not adjusting them 
	N = networks[0].model.layers[l].get_weights()[0]
	if APPLY_BIAS:
		B = networks[0].model.layers[l].get_weights()[1]
	else:
		B = np.zeros(shape[1])

	#add to containers
	curr_weights.append(N)
	curr_bias.append(B)

#used to hold scores to keep running average
running = []

#run through the episodes
for eps in range(NUM_EPS):
	print("Total Frames:", FRAME_COUNT)

	#zero out scores
	scores = np.zeros(NUM_WORKERS)

	#make noise matrix and bias matrix
	noise = []
	bias_noise = []
	print("Generating Noise ", eps)
	for l in range(1,len(networks[0].model.layers)):

		#get shapes
		#TODO: just do this once at the start
		bias_shape = np.array(networks[0].model.layers[l].get_weights()[1]).shape
		shape = np.array(networks[0].model.layers[l].get_weights()[0]).shape

		#create a noise matrix to multiply the base weights by
		#uses polynomial distribution
		N = np.random.randn(NUM_WORKERS, shape[0],shape[1])*SIGMA
		B = np.random.randn(NUM_WORKERS, bias_shape[0])*SIGMA

		#add to containers
		noise.append(N)
		bias_noise.append(B)

	#run workers with their respective noise + base weights
	startProgress("Workers")
	for w in range(NUM_WORKERS):

		#apply noise to base weights
		for l in range(1,len(networks[0].model.layers)):
			new_weights = curr_weights[l-1] + noise[l-1][w]

			if APPLY_BIAS:
				new_bias = curr_bias[l-1] + bias_noise[l-1][w]
			else:
				new_bias = curr_bias[l-1]

			#set the weights on the current worker
			networks[w].model.layers[l].set_weights((new_weights, new_bias))
		#run it and store the score
		scores[w] = networks[w].run()
		#update progress bar
		progress((float(w)/float(NUM_WORKERS))*100)
	endProgress()

	#get standard deviation of each reward
	#add a small amount to account for divide by 0
	std = ((scores - np.mean(scores)) / (np.std(scores) + 1e-5))

	#bookkeeping
	running.append(np.mean(scores))
	curr_score = networks[np.argmax(scores)].run()
	if(curr_score > 250 and scores[np.argmax(scores)] > 250):
		print("Saving")
		networks[np.argmax(scores)].model.save('cartpole_nes.h5')

	print("Avg:", np.mean(scores), "High:", np.amax(scores), "Low:", np.amin(scores), 
		"Running:", sum(running[-100:])/(min(len(running),100)), "Current Best:", curr_score)

	#update the weights
	print("Updating ", eps)
	for l in range(1,len(networks[0].model.layers)):
		weight_dot = noise[l-1]
		bias_dot = bias_noise[l-1]

		weight_dot = np.dot(weight_dot.transpose(1,2,0), std)
		#bias_dot = np.dot(bias_dot.transpose(1,2,0), std)

		curr_weights[l-1] = curr_weights[l-1] + LEARN_RATE/(NUM_WORKERS*SIGMA) * weight_dot
		if APPLY_BIAS:
			curr_bias[l-1] = curr_bias[l-1] + LEARN_RATE/(NUM_WORKERS*SIGMA) * bias_dot
