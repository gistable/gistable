def solve(k, a):
	s = sum(a)

	if s == k:
		return True
	elif s < k:
		return False
	elif len(a) == 1:
		return False
	else:
		for i in range(len(a)):
			temp = a[:i] + a[i+1:]
			if solve(k, temp):
				return True
	return False


a = [2, 43, 6546457, 4, 5, 7, 34, 1]
k = 15
print solve(k, a)