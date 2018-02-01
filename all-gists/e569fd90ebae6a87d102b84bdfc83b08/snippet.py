"""
 _____  ____    ____    __ ______  ____  ___   ____    _____     ____  __ __ 
|     ||    \  /    T  /  ]      Tl    j/   \ |    \  / ___/    |    \|  T  T
|   __j|  D  )Y  o  | /  /|      | |  TY     Y|  _  Y(   \_     |  o  )  |  |
|  l_  |    / |     |/  / l_j  l_j |  ||  O  ||  |  | \__  T    |   _/|  ~  |
|   _] |    \ |  _  /   \_  |  |   |  ||     ||  |  | /  \ | __ |  |  l___, |
|  T   |  .  Y|  |  \     | |  |   j  ll     !|  |  | \    ||  T|  |  |     !
l__j   l__j\_jl__j__j\____j l__j  |____j\___/ l__j__j  \___jl__jl__j  l____/ 

Kevin Nelson -- kpie314@gmail.com -- (c) 2016
"""

def numberOfDecimals(a):
	parts = str(a).split(".")
	if(len(parts)==1):
		return(0)
	if(parts[1]=="0"):
		return(0)
	else:
		return(len(parts[1]))

def scaleToInts(a):
	factor = max([numberOfDecimals(k) for k in a])
	return([int(k*10**factor) for k in a])

def toFraction(top):
	ret.asFraction(top*10**numberOfDecimals(top),10**numberOfDecimals(top))
	return(ret)

def gcd(a,b):#Greates Common Denomonator
	A =int(a) if (a>b) else int(b)
	B =int(b) if (a==A) else int(a)
	c =int(A/B)
	r =A - (c*B)
	return(B if(r == 0)else gcd(r,B))

class fraction():
	top = None
	bottom = None
	def __init__(self):
		top = None
		bottom = None
	def value(self):
		if(self.top == None or self.bottom == None):
			return(None)
		return(float(self.top)/float(self.bottom))
	def display(self):
		return(str(self.top)+"/"+str(self.bottom))
	def fromFraction(self,string):
		parts = string.split("/")
		if(len(parts))!=2:
			raise Exception("InputFormatError")
		try:
			parts[0] = int(parts[0])
			parts[1] = int(parts[1])
		except ValueError:
			raise Exception("InputFormatError")
		self.asFraction(parts[0],parts[1])
	def asFraction(self,a,b):
		top,bottom = scaleToInts([a,b])
		divisor = gcd(top,bottom)
		self.top = top/divisor
		self.bottom = bottom/divisor
	def fraction(self,n):
		factor = numberOfDecimals(n)
		self.asFraction(n*10**factor,10**factor)

def invert(a):
	return 1./a