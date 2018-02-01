import numpy

prime = numpy.ones(limit/2, dtype=numpy.bool)
for i in xrange(3, int(limit**.5) + 1, 2):
	if prime[i/2]:
		prime[i*i/2: : i] = False
primes = 2*prime.nonzero()[0] + 1
primes[0] = 2
