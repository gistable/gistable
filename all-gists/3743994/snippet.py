"""
	what if, when prisoner A kills prisoner B, prisoner A gets prisoner B's sentence taken off theirs?
"""

from random import randrange,random
from itertools import count
from operator import itemgetter

alpha='ABCDEFGHIJKLMNOPQRSTUVWXYZ'

class Killer:
	status = 'imprisoned'
	served = 0
	fights = 0

	def __init__(self,name,sentence):
		self.name = name
		self.sentence = self.skill = sentence
	
	def __str__(self):
		return 'Prisoner %s' % self.name

def prob(a,b):
	return a.skill/(a.skill+b.skill)

def round(num_killers,top_skill):
	population = killers = [Killer(i,randrange(1,top_skill)) for i,x in zip(alpha,range(num_killers))]


	day=0

	while len(killers)>1:
		day+=1
#	print('DAY %i' % day)
		i = randrange(0,len(killers)-1)	#pick a random killer#
		a = killers[i]
		others = killers[:i]+killers[i+1:]
		expected_gains = [b.sentence*prob(a,b) for b in others]
		b = max(zip(expected_gains,others),key=itemgetter(0))[1]
#	print('%s fights %s' % (a,b))
		dead,live = (b,a) if random()<prob(a,b) else (a,b)
		dead.status = 'dead'
		live.sentence -= dead.sentence
		live.fights += 1
#	print('%s died' % dead)
#	print('%s has %i days subtracted from their sentence. They now have %i days to serve.' % (live,dead.sentence,live.sentence))
		for k in killers:
			k.sentence -= 1
			k.served += 1
			if k.sentence<=0:
				k.status = 'released'
#				print('%s is released' % k)
		killers = [k for k in killers if k.status=='imprisoned']

	for k in killers:
		k.status = 'released'

#	print('Nobody is left in prison')
	for k in population:
#	print('Prisoner %s: %s, served %i days of original %i day sentence and fought %i prisoners' % (k.name,k.status,k.served,k.skill,k.fights))
		released = len([k for k in population if k.status=='released'])
#	print('%i prisoners were released' % released)
	return released/len(population)

num_rounds = 100
f=open('killers.csv','w')
for num_killers in range(2,20):
	row = ''
	for top_skill in range(2,100):
		prob_release = sum([round(num_killers,top_skill) for i in range(num_rounds)])/num_rounds
		row+=str(prob_release)+','
	f.write(row+'\n')
f.close()
