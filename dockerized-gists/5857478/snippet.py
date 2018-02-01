def miller_rabin(n, k=10):
	if n == 2:
		return True
	if not n & 1:
		return False

	def check(a, s, d, n):
		x = pow(a, d, n)
		if x == 1:
			return True
		for i in xrange(s - 1):
			if x == n - 1:
				return True
			x = pow(x, 2, n)
		return x == n - 1

	s = 0
	d = n - 1

	while d % 2 == 0:
		d >>= 1
		s += 1

	for i in xrange(k):
		a = randrange(2, n - 1)
		if not check(a, s, d, n):
			return False
	return True

# benchmark of 10000 iterations of miller_rabin(100**10-1); Which is not prime.

# 10000 calls, 11111 per second.
# 74800 function calls in 0.902 seconds