#!/usr/bin/env python
"""
zip.py

Zero-inflated Poisson example using simulated data.

Created by Chris Fonnesbeck on 2008-06-06.
Distributed under the MIT license: http://www.opensource.org/licenses/mit-license.php
"""

import pymc as pm
import numpy as np

# True parameter values
mu_true = 5
psi_true = 0.75
n = 100

# Simulate some data
data = np.array([pm.rpoisson(mu_true)*(np.random.random()<psi_true) for i in range(n)])

# Uniorm prior on Poisson mean
mu = pm.Uniform('mu', 0, 20)
# Beta prior on psi
psi = pm.Beta('psi', alpha=1, beta=1)

@pm.observed(dtype=int, plot=False)
def zip(value=data, mu=mu, psi=psi):
    """ ZIP likelihood """
    
    # Initialise likeihood
    like = 0.0
    
    # Loop over data
    for x in value:
        
        if not x:
            # Zero values
            
            like += np.log((1.-psi) + psi*np.exp(-mu))
            
        else:
            # Non-zero values
            like += np.log(psi) + pm.poisson_like(x, mu)
    
    return like
    
if __name__=="__main__":
    
    M = pm.MCMC(locals())
    M.sample(100000, 50000, verbose=2)