## PyLogis

import numpy as np
import scipy as sp
import matplotlib.pyplot as plt

# Param orders: r, K

def logis(x, y, p):
	est = []
	for time in xrange(0, len(x)):
		num = p[1] * y[0] * np.exp(p[0] * x[time])
		den = p[1] + y[0] * (np.exp(p[0] * x[time]) -1)
		est.append(num/float(den))
	return est

def leastsquare(y, est):
	err = []
	for i in xrange(len(y)):
		err.append( np.power(y[i] - est[i], 2) )
	return np.sum(err)

def pylogis(x, y, npop, ng, f, e, p):
	TimeFit = []
	## Step 1: Initial random parameters
	par = np.empty([npop, len(p)])
	for pop in xrange(npop):
		for pa in xrange(len(p)):
			par[pop,pa] = np.random.normal(loc = p[pa], scale = 1)
	## Step 2: Simuls
	for gen in xrange(ng):
		Fit = []
		for pop in xrange(npop):
			CurrPar = par[pop,:]
			CurrEst = f(x, y, CurrPar)
			CurrErr = e(y, CurrEst)
			Fit.append(CurrErr)
		# Get the best set
		MinFit = np.min(Fit)
		TimeFit.append(MinFit)
		for pop in xrange(npop):
			if Fit[pop] == MinFit:
				p = par[pop,:]
				break
		# New empty parameters
		par = np.empty([npop, len(p)])
		for pop in xrange(npop):
			for pa in xrange(len(p)):
				par[pop,pa] = np.random.normal(loc = p[pa], scale = p[pa] / float(100))
	return p

# Test

Time = np.linspace(0, 35, 80)
Pop = [1]
Par = [0.3, 15]

PopEst = logis(Time, Pop, Par)

for i in xrange(len(PopEst)):
	PopEst[i] = np.random.normal(loc = PopEst[i], scale = PopEst[i] / float(15))

Opt = pylogis(Time, PopEst, 10, 100, logis, leastsquare, [0.01, 12])

PopCal = logis(Time, Pop, Opt)

print Opt

plt.plot(Time, PopCal, 'g-', Time, PopEst, 'bo')
plt.show()