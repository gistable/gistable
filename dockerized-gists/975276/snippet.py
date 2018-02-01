from itertools import product

def score(self, other):
	first = len([speg for speg, opeg in zip(self, other) if speg == opeg])
	return first, sum([min(self.count(j), other.count(j)) for j in 'ABCDEF']) - first

possible = [''.join(p) for p in product('ABCDEF', repeat=4)]
results = [(right, wrong) for right in range(5) for wrong in range(5 - right) if not (right == 3 and wrong == 1)]

def solve(scorefun):
	attempt(set(possible), scorefun, True)

def attempt(S, scorefun, first=False):
	if first:
		a = 'AABB'
	elif len(S) == 1:
		a = S.pop()
	else:
		a = max(possible, key=lambda x: min(sum(1 for p in S if score(p, x) != res) for res in results))

	sc = scorefun(a)

	if sc != (4, 0):
		S.difference_update(set(p for p in S if score(p, a) != sc))
		attempt(S, scorefun)

if __name__ == '__main__':
	import sys
	secret = len(sys.argv) > 1 and sys.argv[1] or input("Please enter a code (four characters, A-F): ")
	if len(secret) == 4 and not (set(secret) - set('ABCDEF')):
		print("Solving...")
		attempts = 0
		def scorefun(x):
			global attempts
			attempts += 1
			sc = score(secret, x)
			print(x, '+'*sc[0] + '-'*sc[1])
			return sc
		solve(scorefun)
		print("It took", attempts, "attempts.")
	else:
		print(secret, "is not a well-formed mastermind code.")