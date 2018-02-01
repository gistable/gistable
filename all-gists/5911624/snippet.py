from scipy.stats.kde import gaussian_kde
import pymc
from math import log
from matplotlib import pyplot

def KernelSmoothing(name, dataset, bw_method=None, lower=float('-inf'), upper=float('inf'), observed=False, value=None):
    '''Create a pymc node whose distribution comes from a kernel smoothing density estimate.'''
    density = gaussian_kde(dataset, bw_method)
    lower_tail = 0
    upper_tail = 0
    if lower > float('-inf'):
        lower_tail = density.integrate_box(float('-inf'),lower)
    if upper < float('inf'):
        upper_tail = density.integrate_box(upper,float('inf'))
    factor = 1.0/(1.0 - lower_tail - upper_tail)
    
    def logp(value):
        if value < lower or value > upper:
            return float('-inf')
        d = density(value)
        if d == 0.0:
            return float('-inf')
        return log(factor*density(value))

    def random():
        result = None
        while result == None:
            result = density.resample(1)[0][0]
            if result < lower or result > upper:
                result = None
        return result
    
    if value == None:
        value = random()
    
    dtype = type(value)
    
    result = pymc.Stochastic(logp = logp,
                             doc = 'A kernel smoothing density node.',
                             name = name,
                             parents = {},
                             random = random,
                             trace = True,
                             value = dataset[0],
                             dtype = dtype,
                             observed = observed,
                             cache_depth = 2,
                             plot = True,
                             verbose = 0)
    return result


###############################################################################
# Use the KernelSmoothing node to update a prior after new information is added
###############################################################################

#True value, used to generate observed values
xtrue = 2                        

#Initial prior to be passed to the KernelSmoothing node
x = pymc.rnormal(0, 0.01, size=5000) 

#Plot the prior
pyplot.figure()
pyplot.hist(x,bins=30)
pyplot.title('Prior Distribution of X')
pyplot.show()

for i in range(10):
    
    #Create the KernelSmoothing node
    X = KernelSmoothing('X', x)
    
    # f(x) = x*x
    Y = X*X
             
    #Create the observed node with data generated from the true distribution
    OBS = pymc.Normal('OBS', Y, 0.1, value=xtrue*xtrue+pymc.rnormal(0,1), observed=True)
    
    #Do the sampling
    model = pymc.Model([X,Y,OBS])
    mcmc = pymc.MCMC(model)
    mcmc.sample(5000)
    
    #Get the posterior sample, to be passed into the KernelSmoothing node on the next iteration
    x = mcmc.trace('X')[:]
    
    #Display the histogram of the posterior distribution
    pyplot.figure()
    pyplot.hist(x,bins=30)
    pyplot.title('Posterior Distribution of X: %d Iterations' % (i+1,))
    pyplot.show()
