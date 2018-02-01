def gen(init, ret, next):
	while True:
		yield ret(init)
		init = next(init)

def myfor(iter, n):
	a = []
	for i, x in enumerate(iter):
		if i == n:
			break
		if x:
			a.append(x)
	return a

print myfor(gen( (3, [2]), lambda (p, ps) : (p - 2 if p - 2 in ps else ''), lambda (p, ps) : (p + 2, (ps if (0 in map(lambda x : p % x, ps)) else ps + [p]))) ,  10)
