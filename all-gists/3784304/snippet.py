from itertools import permutations,product
from operator import itemgetter
from sys import argv
from fractions import Fraction as f

def add(ap,bp):
	(ae,a),(be,b)=ap,bp
	return ('(%s+%s)' % (ae if len(ae) else str(a),be if len(be) else str(b)),a+b)
def sub(ap,bp):
	(ae,a),(be,b)=ap,bp
	return ('(%s-%s)' % (ae if len(ae) else str(a),be if len(be) else str(b)),a-b)
def mul(ap,bp):
	(ae,a),(be,b)=ap,bp
	return ('%s*%s' % (ae if len(ae) else str(a),be if len(be) else str(b)),a*b)
def div(ap,bp):
	((ae,a),(be,b))=(ap,bp)
	return ('%s/%s' % (ae if len(ae) else str(a),be if len(be) else str(b)),a/b)
ops = [add,sub,mul,div]

def comb(nums,ops):
	if len(nums)==1:
		yield nums[0]
		return
	
	for perm in permutations(nums):
		for i in range(1,len(nums)):
			As = set(comb(perm[:i],ops))
			Bs = set(comb(perm[i:],ops))
			for a,b in product(As,Bs):
				for op in ops:
					try:
						yield op(a,b)
					except Exception:
						pass

if len(argv)>1:
	nums = [int(x) for x in argv[1:]]
else:
	nums = [3,3,8,8]
nums = [f(n) for n in nums]
results = set(comb([('',i) for i in nums],ops))
results = sorted(results,key=itemgetter(1))

poss = [a for ae,a in results]
if 24 in poss:
	for ae,a in results:
		if a==24:
			print('24 = %s' % ae)
	print('You can make 24 with these cards.')
else:
	print('You can\'t make 24 with these cards.')
	best = min(poss,key=lambda a: abs(24-a))
	print('Closest is %g' % best)
