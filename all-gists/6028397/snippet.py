#!/usr/bin/env python2
import random
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

MAX_T = 300
MIN_AGE_RELATIONSHIP = 14
BREAKUP_PROBABILITY = 5
NEW_RELATION_PROBABILITY = 10
NOKID_PROBABILITY = 20
MALE_PROBABILITY = 48
DEATH_PROBABILITY_COEFF = 1e-6
WAR_PROBABILITY = 1
WAR_DEATH_PROBABILITY_MALES = 20
WAR_DEATH_PROBABILITY_FEMALES = 5
WAR_MIN_AGE = 18
WAR_MAX_AGE = 40
FAMINE_PROBABILITY = 0.1
FAMINE_DEATH_PROBABILITY = 30
MAX_AGE_DELTA_BETWEEN_PARTNERS_COEFF = 0.5
INITIAL_POPULATION_MALES = 400
INITIAL_POPULATION_FEMALES = 200

def checkProb(prob):
	return random.random() <= prob / 100.0

class Person(object):
	def __init__(self):
		self.age = 0
		self.mother, self.father = None, None
		self.partner = None
		self.n_of_children = 0
		self.generation = 0
		self.noKid = False

		if checkProb(NOKID_PROBABILITY):
			self.childBlock = True
			self.noKid = True
		else:
			self.childBlock = False

	def increaseAge(self):
		self.age += 1

	def increaseChildrenCount(self):
		self.n_of_children += 1

	def setParents(self, mother, father):
		self.mother, self.father = mother, father
		self.generation = max(mother.generation, father.generation) + 1

	def setPartner(self, partner):
		self.partner = partner

	def setChildBlock(self):
		self.childBlock = True

	def releaseChildBlock(self):
		if not self.noKid:
			self.childBlock = False


class Male(Person):
	def __init__(self):
		super(Male, self).__init__()

	def canHaveChild(self):
		if not self.childBlock and self.age > 16 and self.age < 80:
			return True
		return False

class Female(Person):
	def __init__(self):
		super(Female, self).__init__()

	def canHaveChild(self):
		if not self.childBlock and self.age > 14 and self.age < 60 and self.n_of_children < 10:
			return True
		return False

# Initial population
population = set([Male() for _ in range(INITIAL_POPULATION_MALES)] + [Female() for _ in range(INITIAL_POPULATION_FEMALES)])
births_tot, deaths_tot, breakups_tot, new_partners, males, females, max_generation, last_population_count = 0, 0, 0, 0, 0, 0, 0, INITIAL_POPULATION_MALES + INITIAL_POPULATION_FEMALES

def isMale(x):
	return isinstance(x, Male)

def newPartner(x):
	if isMale(x):
		candidates = [y for y in population if (not isMale(y) and abs(y.age-x.age) < MAX_AGE_DELTA_BETWEEN_PARTNERS_COEFF * x.age and y.partner is None and y.age > MIN_AGE_RELATIONSHIP)]
	else:
		candidates = [y for y in population if (isMale(y) and abs(y.age-x.age) < MAX_AGE_DELTA_BETWEEN_PARTNERS_COEFF * x.age and y.partner is None and y.age > MIN_AGE_RELATIONSHIP)]

	if len(candidates) == 0:
		raise Exception("No partner available!")
	
	winner = random.choice(candidates)
	x.setPartner(winner)
	winner.setPartner(x)
	return winner

def newKid(M, F):
	if not (isMale(M) and (not isMale(F))):
		raise Exception("Parents must have opposite sex.")

	M.increaseChildrenCount()
	F.increaseChildrenCount()

	if checkProb(MALE_PROBABILITY):
		newborn = Male()
		M.setChildBlock()
		F.setChildBlock()
	else:
		newborn = Female()

	newborn.setParents(F, M)
	return newborn

population_count, male_count, female_count, avg_age, war_counter, war, famine_counter, famine  = [], [], [], [], 10, False, 5, False
# Main

for t in range(MAX_T):
	print("Time: %d" % t)
	births, deaths = set(), set()

	if war:
		war_counter -= 1
	elif checkProb(WAR_PROBABILITY):
		war = True

	if war_counter == 0:
		war_counter = 10
		war = False

	if famine:
		famine_counter -= 1
	elif checkProb(FAMINE_PROBABILITY):
		famine = True

	if famine_counter == 0:
		famine_counter = 5
		famine = False

	if last_population_count > 0:
		population_count += [last_population_count]
		last_population_count = len(population)
	else:
		print("EXTINCTION at time %d." % t)
		break

	males, females, age_list = 0, 0, []
	for x in population:
		if isMale(x):
			males += 1
		else:
			females += 1
		age_list += [x.age]

	male_count += [males]
	female_count += [females]
	try:
		avg_age += [sum(age_list)/len(age_list)]
	except:
		avg_age += [avg_age[-1]]

	# Rules
	for x in population:

		sex = "MALE" if isMale(x) else "FEMALE"
		x.increaseAge()

		# Death
		if checkProb(DEATH_PROBABILITY_COEFF * x.age ** 4):
			deaths_tot += 1
			if x.partner is not None:
				x.partner.setPartner(None)
				x.partner.releaseChildBlock()
			deaths.add(x)
			# print("Death - %s, age: %d, children: %d - Generation: %d" % (sex, x.age, x.n_of_children, x.generation))
			continue
		if war and x.age >= WAR_MIN_AGE and x.age <= WAR_MAX_AGE and ((isMale(x) and checkProb(WAR_DEATH_PROBABILITY_MALES)) or (not isMale(x) and checkProb(WAR_DEATH_PROBABILITY_FEMALES))):
			deaths_tot += 1
			if x.partner is not None:
				x.partner.setPartner(None)
				x.partner.releaseChildBlock()
			deaths.add(x)
			# print("WAR Death - %s, age: %d, children: %d - Generation: %d" % (sex, x.age, x.n_of_children, x.generation))
			continue
		if famine and checkProb(FAMINE_DEATH_PROBABILITY):
			deaths_tot += 1
			if x.partner is not None:
				x.partner.setPartner(None)
				x.partner.releaseChildBlock()
			deaths.add(x)
			# print("WAR Death - %s, age: %d, children: %d - Generation: %d" % (sex, x.age, x.n_of_children, x.generation))
			continue

		# Breakup?
		if x.partner is not None and checkProb(BREAKUP_PROBABILITY):
			# print("Breakup - %s, age: %d, children: %d FROM PARTNER with age: %d, children: %d" %(sex, x.age, x.n_of_children, x.partner.age, x.partner.n_of_children))

			breakups_tot += 1
			x.partner.releaseChildBlock()
			x.releaseChildBlock()
			x.partner.setPartner(None)
			x.setPartner(None)

		# Check partnership
		if x.partner is None and x.age > MIN_AGE_RELATIONSHIP and checkProb(NEW_RELATION_PROBABILITY):
			try:
				partner = newPartner(x)
				# print("New relationship - %s, age: %d, children: %d WITH PARTNER with age: %d, children: %d" %(sex, x.age, x.n_of_children, x.partner.age, x.partner.n_of_children))
				new_partners += 1
			except:
				partner = None
		else:
			partner = x.partner

		# Reproduction
		if partner is not None and x.canHaveChild() and partner.canHaveChild() and checkProb((200 * MIN_AGE_RELATIONSHIP) / (x.age + partner.age)):
			births_tot += 1

			try:
				if isMale(x):
					newborn = newKid(x, partner)
				else:
					newborn = newKid(partner, x)
			except:
				continue

			newborn_sex = "MALE" if isMale(newborn) else "FEMALE"
			max_generation = max(max_generation, newborn.generation)

			# print("Birth - %s - Parents: %s, age: %d, children: %d WITH PARTNER with age: %d, children: %d" %(newborn_sex, sex, x.age, x.n_of_children, partner.age, partner.n_of_children))

			births.add(newborn)

	population = (population - deaths).union(births)

generations = Counter()
males, females = 0, 0
for x in population:
	if isMale(x):
		males += 1
	else:
		females += 1
	generations[x.generation] += 1

# Print info

print("%d Males and %d Females." % (males, females))
print("%d births and %d deaths." % (births_tot, deaths_tot))
print("%d breakups and %d new relationships." % (breakups_tot, new_partners))
print("Generations:")
print(generations)
print("Max generation reached: %d." % (max_generation))

# Create the plot

plt.figure(1)
plt.subplot(211)
plt.plot(population_count, 'g', label='Total population')
plt.plot(male_count, 'b', label='Males')
plt.plot(female_count, 'r', label='Females')
plt.legend(loc=1)

plt.subplot(212)
plt.plot(avg_age, 'y', label='Avg. age')

plt.legend(loc=4)
plt.show()
