def gcd(a, b):
	while b:
		a, b = b, a%b
	return a
for _ in xrange(int(raw_input())):
	n = int(raw_input())
	ans = n/2
	while gcd(n, ans) != 1:
		ans -= 1
	print ans