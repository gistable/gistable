from numpy import *
from scipy.stats import beta
import random


class BetaBandit(object):
    def __init__(self, num_options=2, prior=None):
        self.trials = zeros(shape=(num_options,), dtype=int)
        self.successes = zeros(shape=(num_options,), dtype=int)
        self.num_options = num_options
        if prior is None:
            prior = [ (1.0, 1.0) for i in range(num_options)]
        self.prior = prior

    def add_result(self, trial_id, success):
        self.trials[trial_id] = self.trials[trial_id] + 1
        if (success):
            self.successes[trial_id] = self.successes[trial_id] + 1

    def get_recommendation(self):
        sampled_theta = []
        for i in range(self.num_options):
            #Construct beta distribution for posterior
            dist = beta(self.prior[i][0]+self.successes[i],
                        self.prior[i][1]+self.trials[i]-self.successes[i])
            #Draw sample from beta distribution
            sampled_theta += [ dist.rvs() ]
        # Return the index of the sample with the largest value
        return sampled_theta.index( max(sampled_theta) )

prior_params = [(9.0,20.0), (4.0,20.0)]
priors = [beta(*x) for x in prior_params]

def gain(theta, choice):
    if (random.random() < theta[choice]):
        return 1
    else:
        return 0

def gain_bandit(theta, num_trials):
    bb = BetaBandit(2)
    g = 0
    for i in range(int(num_trials)):
        choice = bb.get_recommendation()
        g += gain(theta, choice)
    return g

def gain_prior(theta, num_trials):
    bb = BetaBandit(2, prior_params)
    g = 0
    for i in range(int(num_trials)):
        choice = bb.get_recommendation()
        g += gain(theta, choice)
    return g

num_trials = 50.0
N = 2000
tg = 0
tgb = 0

for i in range(N):
    theta = [ p.rvs() for p in priors]
    tg += gain_bandit(theta, num_trials) / num_trials
    tgb += gain_prior(theta, num_trials) / num_trials

print "Base gain: " + str(float(tg)/N)
print "Prior gain: " + str(float(tgb)/N)
