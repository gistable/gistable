def NOT(a):
	return (1 - a)

def AND(a,b):
	return a * b	
	
def OR(a,b):
	return a + b
		
def NAND(a,b):
	return NOT(AND(a,b))

def NOR(a,b):
	return NOT(OR(a,b))

def XOR(a,b):
	x = OR(a,b)
	y = NAND(a,b)
	return AND(x,y)

def halfAdder(a,b):
	x = XOR(a,b)
	y = AND(a,b)
	return x,y

def fullAdder(a,b,c):
	x = halfAdder(a,b)
	y = halfAdder(x[0],c)
	z = OR(x[1], y[1])
	return (y[0],z)