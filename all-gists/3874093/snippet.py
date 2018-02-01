from math import sqrt
class Vector:
	data  = []
	def __init__(self,items):
		self.data = items

	def __repr__(self):
		return repr(self.data)

	def __add__(self,other):
		temp = []
		for j in range(len(self.data)):
			temp.append(self.data[j] + other.data[j])
		return Vector(temp)

	def __getitem__(self,a):
		return self.data[a]

	def __setitem__(self,a,b):
		self.data[a] = b


	def magnitude(self):
		temp = 0
		for j in range(len(self.data)):
			temp += self.data[j] * self.data[j]
		return sqrt(temp)
			
	def dot(self,other):
		temp = 0
		for j in range(len(self.data)):
			temp += self.data[j] * other.data[j]
		return temp
	def cosine(self,other):
		temp = self.dot(other)
		return temp / (self.magnitude() * other.magnitude())
	
	def remove(self,pos):
		self.data[pos] = 0