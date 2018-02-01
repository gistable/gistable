#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division


my_things = {
	'hello': 34,
	'a': True,
	'b': 56.874
}


my_numbers = [23, 'hello', 56.5]

my_set = {1,2,3,4}

my_dups_list = ['d', 4, 'd', 4, 4, 67, 8, 8, 1]

no_dups = list(set(my_dups_list))

print my_things
print my_numbers

a = [1,2,3]

for i in range(1, 20):
	a.append(i)

print a

def myfunc(a,b):
	return a + b

x = myfunc

def __apply(f, a, b):
	return f(a,b)

my_list = [x * 2 for x in range(1, 20)]


def myMult(operand1=0, operand2=0):
	return operand1 * operand2


def myCrazyFunc(**kwargs):
	print kwargs

def myCrazierFunc(a, b, *args, **kwargs):
	print args
	print kwargs

def kwargf(**kwargs):
	if 'x' in kwargs:
		x = kwargs['x']
		x = kwargs.pop('x')




def mySum(a,b, *args):
	return a * b / sum(args)





class ComplexNumber(object):

	def __init__(self, real, imaginary):
		self.real = real
		self.imaginary = imaginary

	def __add__(self, other):
		return ComplexNumber(self.real + other.real, self.imaginary + other.imaginary)

	@staticmethod
	def one():
		return ComplexNumber(1,1)

	def __setZero(self):
		self.real = self.imaginary = 0

	def __unicode__(self):
		return '{} + {}i'.format(self.real, self.imaginary)

	def __str__(self):
		return self.__unicode__()





class Person(object):
	name = 'Rahul'
	age = '24'

class Warrior(ComplexNumber, Person):
	weapon = 'Sword'


class Animal(object):
	name = 'random Animal'
	def get_name(self):
		return self.name


class Dog(Animal):

	def get_name(self):
		return super(Dog, self).get_name()


c = ComplexNumber(1, 3)

print c