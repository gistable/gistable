#!/usr/bin/python

import random

class Die:
	def __init__(self,sides):
		self.sides = sides
		self.facet = False

	def __str__(self):
		text = 'd' + str(self.sides)
		if self.facet != False: text += ' (' + str(self.facet) + ')'
		return text

	def roll(self):
		self.facet = random.randint(1,self.sides)
		return self.facet

class Dice:
	def __init__(self):
		self.dice = []
		self.lastrolled = ''

	def __str__(self):
		text = "A bag of dice containing: "
		for die in self.dice:
			text += str(die) + ', '
		return text

	def adddie(self,die):
		self.dice.append(die)

	def adddice(self,dice):
		for die in dice:
			self.adddie(die)
		return self

	def setdice(self, *dice):
		self.__init__()
		self.adddice(dice)
		return self

	def roll(self):
		for die in self.dice:
			die.roll()
		return self

	def look(self):
		a = []
		for die in self.dice:
			a.append(str(die.facet))
		return "The dice show " + ', '.join(a) + "."

def createdice(die):
	defaults = { 'sides':6, 'number':1 }
	if isinstance(die, str):
		try:
			number, sides = die.split('d')
		except ValueError:
			try:
				number, sides = 1, int(die)
			except ValueError:
				number, sides = 1, defaults['sides']
	elif isinstance(die, tuple):
		number, sides = die
	number, sides = int(number), int(sides)
	dice = []
	for i in range(number):
		dice.append( Die(sides) )
	return dice

if __name__ == '__main__':
	x = Dice()
	print x
	print x.adddice(createdice('3d6'))
	print x.adddice(createdice('2d2'))
	print x.roll().look()
	print x