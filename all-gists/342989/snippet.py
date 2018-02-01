import numpy as np
import pymc
import pdb

def unconditionalProbability(Ptrans):
   """Compute the unconditional probability for the states of a
   Markov chain."""

   m = Ptrans.shape[0]

   P = np.column_stack((Ptrans, 1. - Ptrans.sum(axis=1)))

   I = np.eye(m)
   U = np.ones((m, m))
   u = np.ones(m)

   return np.linalg.solve((I - P + U).T, u)

data = np.loadtxt('test_data.txt',
                 dtype=np.dtype([('state', np.uint8),
                                 ('emission', np.float)]),
                 delimiter=',',
                 skiprows=1)

# Two state model for simplicity.
N_states = 2
N_chain = len(data)

# Transition probability stochastic
theta = np.ones(N_states) + 1.

def Ptrans_logp(value, theta):
   logp = 0.
   for i in range(value.shape[0]):
       logp = logp + pymc.dirichlet_like(value[i], theta)
   return logp

def Ptrans_random(theta):
   return pymc.rdirichlet(theta, size=len(theta))

Ptrans = pymc.Stochastic(logp=Ptrans_logp,
                        doc='Transition matrix',
                        name='Ptrans',
                        parents={'theta': theta},
                        random=Ptrans_random)

#Hidden states stochastic
def states_logp(value, Ptrans=Ptrans):
    
    if sum(value>1):
        return -np.inf

    P = np.column_stack((Ptrans, 1. - Ptrans.sum(axis=1)))

    Pinit = unconditionalProbability(Ptrans)

    logp = pymc.categorical_like(value[0], Pinit)

    for i in range(1, len(value)):
       try:
          logp = logp + pymc.categorical_like(value[i], P[value[i-1]])
       except:
          pdb.set_trace()

    return logp

def states_random(Ptrans=Ptrans, N_chain=N_chain):
   P = np.column_stack((Ptrans, 1. - Ptrans.sum(axis=1)))

   Pinit = unconditionalProbability(Ptrans)

   states = np.empty(N_chain, dtype=np.uint8)

   states[0] = pymc.rcategorical(Pinit)

   for i in range(1, N_chain):
       states[i] = pymc.rcategorical(P[states[i-1]])

   return states

states = pymc.Stochastic(logp=states_logp,
                        doc='Hidden states',
                        name='states',
                        parents={'Ptrans': Ptrans},
                        random=states_random,
                        dtype=np.uint8)

# Gaussian emission parameters
mu = pymc.Normal('mu', 0., 1.e-6, value=np.random.randn(N_states))
sigma = pymc.Uniform('sigma', 0., 100.,
value=np.random.rand(N_states))

y = pymc.Normal('y', mu[states], 1./sigma[states]**2,
value=data['emission'], observed=True)