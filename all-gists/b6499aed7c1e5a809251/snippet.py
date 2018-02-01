# CSci 1913 Lab Section 06
# Lab 1
# Ryan Sjostrand and Benjamin Pankow



def left(e):
	return e[0]

def op(e):
	return e[1]

def right(e):
	return e[2]


def isInside(v, e):
	if type(e) is str or type(e) is int:
		return e == v

	else:
		return isInside(v, left(e)) or isInside(v, right(e))

def solve(v, q):
	if isInside(v, left(q)):
		return solving(v, q)
	elif isInside(v, right(q)):
		return solving(v, [right(q), op(q), left(q)])
	else:
		return None

def solving(v, q):
	if (v == left(q)):
		return q
	else:
		# See dictionary below, this gets the corresponding solving function to the operator on the left side
		return operations[op(left(q))](v, q)

def solvingAdd(v, q):
	a = left(left(q))
	b = right(left(q))
	c = right(q)

	if isInside(v, a):
		newQ = [a, "=", [c, "-", b]]
		return solving(v, newQ)
	elif isInside(v, b):
		newQ = [b, "=", [c, "-", a]]
		return solving(v, newQ)
	else:
		return None

def solvingSubtract(v, q):
	a = left(left(q))
	b = right(left(q))
	c = right(q)

	if isInside(v, a):
		newQ = [a, "=", [c, "+", b]]
		return solving(v, newQ)
	elif isInside(v, b):
		newQ = [b, "=", [a, "-", c]]
		return solving(v, newQ)
	else:
		return None

def solvingMultiply(v, q):
	a = left(left(q))
	b = right(left(q))
	c = right(q)

	if isInside(v, a):
		newQ = [a, "=", [c, "/", b]]
		return solving(v, newQ)
	elif isInside(v, b):
		newQ = [b, "=", [c, "/", a]]
		return solving(v, newQ)
	else:
		return None

def solvingDivide(v, q):
	a = left(left(q))
	b = right(left(q))
	c = right(q)

	if isInside(v, a):
		newQ = [a, "=", [c, "*", b]]
		return solving(v, newQ)
	elif isInside(v, b):
		newQ = [b, "=", [a, "/", c]]
		return solving(v, newQ)
	else:
		return None

# Dictionary that links operator characters to their corresponding functions
operations = {
	"+" : solvingAdd,
	"-" : solvingSubtract,
	"*" : solvingMultiply,
	"/" : solvingDivide
}

#
#  TESTS. Test the equation solver for CSci 1913 Lab 1
#
#    James B. Moen
#    18 Sep 15
#

#  Each PRINT is followed by a comment that shows what must be printed if your
#  program works correctly.

print(isInside('x', 'x'))                          #  True
print(isInside('x', 'y'))                          #  False
print(isInside('x', ['x', '+', 'y']))              #  True
print(isInside('x', ['a', '+', 'b']))              #  False
print(isInside('x', [['m', '*', 'x'], '+', 'b']))  #  True

print(solve('x', [['a', '+', 'x'], '=', 'c']))  #  ['x', '=', ['c', '-', 'a']]
print(solve('x', [['x', '+', 'b'], '=', 'c']))  #  ['x', '=', ['c', '-', 'b']]

print(solve('x', [['a', '-', 'x'], '=', 'c']))  #  ['x', '=', ['a', '-', 'c']]
print(solve('x', [['x', '-', 'b'], '=', 'c']))  #  ['x', '=', ['c', '+', 'b']]

print(solve('x', [['a', '*', 'x'], '=', 'c']))  #  ['x', '=', ['c', '/', 'a']]
print(solve('x', [['x', '*', 'b'], '=', 'c']))  #  ['x', '=', ['c', '/', 'b']]

print(solve('x', [['a', '/', 'x'], '=', 'c']))  #  ['x', '=', ['a', '/', 'c']]
print(solve('x', [['x', '/', 'b'], '=', 'c']))  #  ['x', '=', ['c', '*', 'b']]

print(solve('x', ['y', '=', [['m', '*', 'x'], '+', 'b']]))
# ['x', '=', [['y', '-', 'b'], '/', 'm']
print(solve("y", [["x", "-", 5], "=", [[["y", "-", ["x", "+", 3]], "-", 50], "/", ["x", "+", 5]]]))