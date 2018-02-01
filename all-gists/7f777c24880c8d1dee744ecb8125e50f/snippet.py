"""
check out http://kushalvyas.github.io/gen_8Q.html#gen_8Q

@file : queens.py 

Illustration of 8 queens using GA - evolution

"""

import numpy as np
import sys



nQueens = 8
STOP_CTR = 28
MUTATE = 0.000001
MUTATE_FLAG = True
MAX_ITER = 100000
POPULATION = None

class BoardPosition:
	def __init__(self):
		self.sequence = None
		self.fitness = None
		self.survival = None
	def setSequence(self, val):
		self.sequence = val
	def setFitness(self, fitness):
		self.fitness = fitness
	def setSurvival(self, val):
		self.survival = val
	def getAttr(self):
		return {'sequence':sequence, 'fitness':fitness, 'survival':survival}

def fitness(chromosome = None):
	"""
	returns 28 - <number of conflicts>
	to test for conflicts, we check for 
	 -> row conflicts
	 -> columnar conflicts
	 -> diagonal conflicts
	 
	The ideal case can yield upton 28 arrangements of non attacking pairs.
	for iteration 0 -> there are 7 non attacking queens
	for iteration 1 -> there are 6 no attacking queens ..... and so on 

	Therefore max fitness = 7 + 6+ 5+4 +3 +2 +1 = 28

	hence fitness val returned will be 28 - <number of clashes>

	"""

	# calculate row and column clashes
	# just subtract the unique length of array from total length of array
	# [1,1,1,2,2,2] - [1,2] => 4 clashes
	clashes = 0;
	row_col_clashes = abs(len(chromosome) - len(np.unique(chromosome)))
	clashes += row_col_clashes

	# calculate diagonal clashes
	for i in range(len(chromosome)):
		for j in range(len(chromosome)):
			if ( i != j):
				dx = abs(i-j)
				dy = abs(chromosome[i] - chromosome[j])
				if(dx == dy):
					clashes += 1


	return 28 - clashes	


def generateChromosome():
	# randomly generates a sequence of board states.
	global nQueens
	init_distribution = np.arange(nQueens)
	np.random.shuffle(init_distribution)
	return init_distribution

def generatePopulation(population_size = 100):
	global POPULATION

	POPULATION = population_size

	population = [BoardPosition() for i in range(population_size)]
	for i in range(population_size):
		population[i].setSequence(generateChromosome())
		population[i].setFitness(fitness(population[i].sequence))

	return population


def getParent():
	globals()	
	parent1, parent2 = None, None
	# parent is decided by random probability of survival.
	# since the fitness of each board position is an integer >0, 
	# we need to normaliza the fitness in order to find the solution
	
	summation_fitness = np.sum([x.fitness for x in population])
	for each in population:
		each.survival = each.fitness/(summation_fitness*1.0)

	while True:
		parent1_random = np.random.rand()
		parent1_rn = [x for x in population if x.survival <= parent1_random]
		try:
			parent1 = parent1_rn[0]
			break
		except:
			pass

	while True:
		parent2_random = np.random.rand()
		parent2_rn = [x for x in population if x.survival <= parent2_random]
		try:
			t = np.random.randint(len(parent2_rn))
			parent2 = parent2_rn[t]
			if parent2 != parent1:
				break
			else:
				print "equal parents"
				continue
		except:
			print "exception"
			continue

	if parent1 is not None and parent2 is not None:
		return parent1, parent2
	else:
		sys.exit(-1)

def reproduce_crossover(parent1, parent2):
	globals()
	n = len(parent1.sequence)
	c = np.random.randint(n, size=1)
	child = BoardPosition()
	child.sequence = []
	child.sequence.extend(parent1.sequence[0:c])
	child.sequence.extend(parent2.sequence[c:])
	child.setFitness(fitness(child.sequence))
	return child


def mutate(child):
	"""	
	- according to genetic theory, a mutation will take place
	when there is an anomaly during cross over state

	- since a computer cannot determine such anomaly, we can define 
	the probability of developing such a mutation 

	"""
	if child.survival < MUTATE:
		c = np.random.randint(8)
		child.sequence[c] = np.random.randint(8)
	return child

def GA(iteration):
	print " #"*10 ,"Executing Genetic  generation : ", iteration , " #"*10
	globals()
	newpopulation = []
	for i in range(len(population)):
		parent1, parent2 = getParent()
		# print "Parents generated : ", parent1, parent2

		child = reproduce_crossover(parent1, parent2)

		if(MUTATE_FLAG):
			child = mutate(child)

		newpopulation.append(child)
	return newpopulation


def stop():
	globals()
	# print population[0], " printing population[0]"
	fitnessvals = [pos.fitness for pos in population]
	if STOP_CTR in fitnessvals:
		return True
	if MAX_ITER == iteration:
		return True
	return False



population = generatePopulation(1000)

print "POPULATION size : ", population

iteration = 0;
while not stop():
	# keep iteratin till  you find the best position
	population = GA(iteration)
	iteration +=1 

print "Iteration number : ", iteration
for each in population:
	if each.fitness == 28:
		print each.sequence