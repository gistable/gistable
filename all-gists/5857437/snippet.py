def fermat(n):
	if n == 2:
		return True
	if not n & 1:
		return False
	return pow(2, n-1, n) == 1
	
# benchmark of 10000 iterations of fermat(100**10-1); Which is not prime.

# 10000 calls, 21141 per second.
# 20006 function calls in 0.481 seconds