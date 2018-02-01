#Code from http://fmota.eu/, great!
class Monoid:
	def __init__(self, null, lift, op):
		self.null = null
		self.lift = lift
		self.op   = op

	def fold(self, xs):
		if hasattr(xs, "__fold__"):
			return xs.__fold__(self)
		else:
			return reduce(self.op, (self.lift(x) for x in xs), self.null)

	def __call__(self, *args):
		return self.fold(args)

	def star(self):
		return Monoid(self.null, self.lift, self.op)

summ   = Monoid(0,  lambda x: x,      lambda a,b: a+b)
joinm  = Monoid('', lambda x: str(x), lambda a,b: a+b)
listm  = Monoid([], lambda x: [x],    lambda a,b: a+b)
tuplem = Monoid((), lambda x: (x,),   lambda a,b: a+b)
lenm   = Monoid(0,  lambda x: 1,      lambda a,b: a+b)
prodm  = Monoid(1,  lambda x: x,      lambda a,b: a*b)