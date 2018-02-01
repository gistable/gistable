import gym
import numpy as np 
import matplotlib.pyplot as plt
env = gym.make('CartPole-v0')
env.render(close=True)
#vector of means(mu) and standard dev(sigma) for each paramater
mu=np.random.uniform(size=state.shape)
sigma=np.random.uniform(low=0.001,size=state.shape)


def noisy_evaluation(env,W,render=False,):
	""" uses parameter vector W to choose policy for 1 episode,
	 returns reward from that episode"""
	reward_sum=0
	state=env.reset()
	t=0
	while True:
	  t+=1
	  action=int(np.dot(W,state)>0)#use parameters/state to choose action
	  state,reward,done,info=env.step(action)
	  reward_sum+=reward
	  if render and t%3==0: env.render()
	  if done or t > 205:
	  	#print("finished episode, got reward:{}".format(reward_sum)) 
	  	break

	return reward_sum

def init_params(mu,sigma,n):
	"""take vector of mus, vector of sigmas, create matrix such that """
	l=mu.shape[0]
	w_matrix=np.zeros((n,l))
	for p in range(l):
			w_matrix[:,p]=np.random.normal(loc=mu[p],scale=sigma[p]+1e-17,size=(n,))
	return w_matrix

running_reward=0
n=40;p=8;n_iter=20;render=False
env.monitor.start('/tmp/cartpole-experiment-1',force=True)

state=env.reset()
i=0
plt.ion()
while i < n_iter:
	#initialize an array of parameter vectors
	#wvector_array=np.random.normal(loc=mu,scale=sigma,size=(n,state.shape[0]))
	wvector_array=init_params(mu,sigma,n)
	reward_sums=np.zeros((n))
	for k in range(n):
		#sample rewards based on policy parameters in row k of wvector_array
		reward_sums[k]=noisy_evaluation(env,wvector_array[k,:],render)
	env.render(close=True)
	#sort params/vectors based on total reward of an episode using that policy
	rankings=np.argsort(reward_sums)
	#pick p vectors with highest reward
	top_vectors=wvector_array[rankings,:]
	top_vectors=top_vectors[-p:,:]
	print("top vectors shpae:{}".format(top_vectors.shape))
	#fit new gaussian from which to sample policy
	#top_vectors=top_vectors.reshape(top_vectors.shape[0],top_vectors.shape[2])
	for q in range(top_vectors.shape[1]):
		#print("mean here:{}")
		mu[q]=top_vectors[:,q].mean()
		#print("sigma:{}".format(top_vectors[q,:].std()))
		sigma[q]=top_vectors[:,q].std()
	
	running_reward=0.99*running_reward + 0.01*reward_sums.mean()
	print("#############################################################################")
	print("iteration:{},mean reward:{}, running reward mean:{} \n"
		" reward range:{} to {},".format(
		    i, reward_sums.mean(),running_reward,reward_sums.min(),reward_sums.max(),
		    ))
	plt.scatter(i,reward_sums.mean())
	plt.scatter(i,running_reward,color='r')
	plt.pause(0.001)
	i+=1
env.monitor.close()

gym.upload('/tmp/cartpole-experiment-1',api_key='YOUR API KEY HERE!!!')


env.render(close=True)