w = [1,4,2,5] # Some data
w_max = max(w)
n = len(w)

while True:
	idx = random.randrange(n)
	u = w_max*random.random()
	if u <= w[idx]:
		break
print idx