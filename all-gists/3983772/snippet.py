from itertools import product

times = product(range(24),range(60))

primes = [2,3,5,7,11,13,17,19,23]	#we only need primes < 24

def cancel(a,b):
	if a==b==0:
		return (0,0)
	for p in primes:
		if a%p==b%p==0:
			return cancel(a//p,b//p)	# a//p is integer division
	return (a,b)

ratios = set(cancel(a,b) for a,b in times)
print('%i unique ratios out of %i unique times' % (len(ratios),24*60) )
