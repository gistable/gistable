import inspect


# Callable class to wrap functions
class F:
  def __init__(self, func, *args):
		self.func = func
		self.args = args

	# Currying
	def __call__(self, *args):
		try:
			nargs	= len(inspect.getargspec(self.func)[0])
		except TypeError:
			nargs	= 1
		dnargs	= nargs - len(args) - len(self.args)
		if dnargs == 0:
			return self.func(*(self.args+args))

		return F(self.func, *(self.args+args))

	# Composition
	def __mul__(f, g):
		return F(lambda a: f(g(a)))

if __name__ == "__main__":

	add = lambda a, b: a + b

	assert add(1,2) == 3

	# Turn 'add' into a fully Functional function
	add	= F(add)

	# Still works as normally
	assert add(1,2) == 3

	# Now we can do currying
	assert add(1)(2) == 3
	assert add()(1,2) == 3
	assert add()(1)(2) == 3

	add_one = add(1)
	add_two = add(2)

	assert add_one(10) == 11
	assert add_two(10) == 12
	
	# We can compose two functions
	# add_three(x) = add_one(add_two(x))
	add_three = add_one * add_two

	assert add_three(5) == 8

	# Let's compose three functions
	rsort = F(list) * reversed * sorted

	assert rsort([1,5,3,2,0,4]) == [5,4,3,2,1,0]