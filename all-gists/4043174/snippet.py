# Simulator for the simple Boltzmann machine of Coursera NN Lecture 11e
# Christian Jauvin - cjauvin@gmail.com

from collections import defaultdict
import numpy as np

# weights
w_v1_h1 = 2
w_h1_h2 = -1
w_h2_v2 = 1

N = 1000 # number of sims to run
M = 1000 # number of updates to perform for each
T = 1    # temperature

def delta_E(i, v1, v2, h1, h2):
    return [h1 * w_v1_h1,                   # v1
            h2 * w_h2_v2,                   # v2
            v1 * w_v1_h1 + h2 * w_h1_h2,    # h1
            h1 * w_h1_h2 + v2 * w_h2_v2][i] # h2

def prob_s_on(i, T, conf):
    return 1 / (1 + np.exp(-delta_E(i, *conf) / T))

confs = defaultdict(int) # counter for each conf

for n in range(N):
    conf = np.random.random_integers(0, 1, 4) # random starting conf
    for i in np.random.random_integers(0, 3, M): # stream of random updates
        conf[i] = 1 if np.random.random() < prob_s_on(i, T, conf) else 0
    confs[tuple(conf)] += 1

# show resulting probs
for conf, n in sorted(confs.items(), reverse=True):
    print conf, float(n) / N