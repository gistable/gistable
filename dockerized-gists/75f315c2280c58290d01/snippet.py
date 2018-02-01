class Ringloop (object):
	
#"A class that loops as a ring, it recursively calls function one until a condition is True, then recursively calls function two until the second condition is True. The loop keeps iterating in a ring across the two functions until the end condition is satisfied, and the final value is returned."
	
	def __init__(self, value, f1, f2, c1, c2, end):
		self.value = value
		self.f1 = f1 #first function
		self.f2 = f2 #second function
		self.c1 = c1 #condition for checkpoint1
		self.c2 = c2 #condition for checkpoint2
		self.end = end #condition to return the value
	def checkpoint1(self):
		if self.end(self.value) == True:
			Ringloop.endloop(self)
		else: 
			if self.c1(self.value) == True:
				Ringloop.function2(self)
			if self.c1(self.value) == False:
				Ringloop.function1(self)
	def checkpoint2(self):
		if self.end(self.value) == True:
			Ringloop.endloop(self)
		else: 
			if self.c2(self.value) == True:
				Ringloop.function1(self)
			if self.c2(self.value) == False:
				Ringloop.function2(self)
	def function1(self):
		self.value = self.f1(self.value)
		Ringloop.checkpoint1(self)
	def function2(self):
		self.value = self.f2(self.value)
		Ringloop.checkpoint2(self)
	def startloop(self):
		Ringloop.checkpoint1(self)
	def endloop(self):
		print(self.value)
		return self.value


	
	
	
