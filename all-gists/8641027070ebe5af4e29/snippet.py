import math
import random
#A class and corresponding function that allows you to construct a dictionary that contains all random combinations of a particular list, of some length, count. Each combo is stored as a set in a random order. 


class combogenerator (object):
	
	def __init__(self):
		self.dictone = []
		self.list = []
		self.randset = []
		self.combo_dict = {}
	def loadlist(self, list): #loads a list into position for iteration.
		for x in list:
			self.dictone.append(x)
		return self.dictone
	def updatedict(self): #clears all index in list.
		for x in self.list:
			self.dictone.append(x)
		self.list = []
	def rand_combo_list(self, length): #gives one random combination of a list.
		while len(self.list) < length:
			for x in self.dictone:
				pick = random.randrange(len(self.dictone))
				self.randset.append(self.dictone[pick])
				for y in self.randset:
					first_let = int(str(y)[0])
					if y in self.list:
						self.randset.remove(y)
					if y not in self.list:
						self.list.append(y)
						self.randset = []
						self.dictone.remove(y)
		return self.list
	def combo_set_into_dict(self, count): #returns a set into a dictionary entry that contains one combo of the list.
		combo_number = len(self.combo_dict) + 1
		combogenerator.rand_combo_list(self, count)
		setlist = set(self.list[:])
		if setlist not in self.combo_dict.values():
			self.combo_dict.update({combo_number:setlist})
			combogenerator.updatedict(self)
		else:
			combogenerator.updatedict(self)
		return self.combo_dict
	def generate_all_combos(self, count): #prints a dictionary of set values to determine all combinations of a list.
		length = len(self.dictone)
		max_combos = math.factorial(length)/(math.factorial(count)*math.factorial(length - count))
		while len(self.combo_dict) < max_combos:
			combogenerator.combo_set_into_dict(self, count)
		for v in self.combo_dict.values():
			print list(v)

def combo_iterator(list, count):
	if count < len(list):
		c = combogenerator()
		combogenerator.loadlist(c, list)
		combogenerator.generate_all_combos(c, count)
	else: 
		print('You must choose combinations that are shorter than your list')
