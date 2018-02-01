#!/usr/bin/python

import sys
import itertools

POWER_EVAL = .6
TOUGHNESS_EVAL = .4
DOUBLE_STRIKE_MULT = 1.5
DEATHTOUCH_EVAL = 1
FLYING_EVAL = 1
FIRST_STRIKE_EVAL = 1
INDESTRUCTIBLE_EVAL = 1.5
LIFELINK_EVAL = 1
MENACE_EVAL = .5
REACH_EVAL = .375
TRAMPLE_EVAL = .25
CREATURE_EVAL = .5
LIFE_EVAL = .3

def get_digit(value, base, index):
	return (value / pow(base, index)) % base

def combine_results(r1, r2, max):
	for key in r2:
		if not key in r1:
			r1[key] = r2[key]
		# Better score.
		if max and r2[key].score > r1[key].score:
			r1[key] = r2[key]
		if not max and r2[key].score < r1[key].score:
			r1[key] = r2[key]
		# Equal score, but lower number of attackers and blockers.
		if r1[key].score == r2[key].score:
			r1_combatant_count = len(r1[key].attackers) + sum(map(len, r1[key].blockers))
			r2_combatant_count = len(r2[key].attackers) + sum(map(len, r2[key].blockers))
			if r2_combatant_count < r1_combatant_count:
				r1[key] = r2[key]

def print_results(r):
	for key in sorted(r.iterkeys()):
		print key
		print r[key]

class Result:
	def __init__(self, p1, p2, attackers, blockers, damage, score):
		self.p1 = p1
		self.p2 = p2
		self.attackers = attackers
		self.blockers = blockers
		self.damage = damage
		self.score = score

	def __str__(self):
		string = ''
		for i in range(0, len(self.attackers)):
			attacker = self.attackers[i]
			string += '\n\tP1 attacks with ' + `p1[attacker]` + '.'
			for blocker in self.blockers[i]:
				string += '\n\t\tP2 blocks with ' + `p2[blocker]` + '.'
			if len(self.blockers[i]) == 0:
				string += '\n\t\tP2 doesn\'t block.'
		if len(self.attackers) == 0:
			string = 'P1 doesn\'t attack.'
		string += '\n\tDamage to P2: ' + `self.damage`;
		score_string = 'MAX' if self.score > 999999999 else '%.2f' % self.score
		string += '\n\tScore: ' + score_string;
		return '\t' + string.strip()

	def __repr__(self):
		return str(self)

class Creature:
	def __init__(self, power, toughness, keywords = ''):
		# Characteristics
		self.p = power
		self.t = toughness
		# Keywords
		self.dt = False
		self.ds = False
		self.f = False
		self.fs = False
		self.i = False
		self.l = False
		self.m = False
		self.r = False
		self.tr = False
		if keywords == '' or keywords == None:
			return
		keywords = keywords.split(',')
		for keyword in keywords:
			keyword = keyword.strip()
			if keyword == 'dt':
				self.dt = True
			if keyword == 'ds':
				self.ds = True
			if keyword == 'f':
				self.f = True
			if keyword == 'fs':
				self.fs = True
			if keyword == 'i':
				self.i = True
			if keyword == 'l':
				self.l = True
			if keyword == 'm':
				self.m = True
			if keyword == 'r':
				self.r = True
			if keyword == 'tr':
				self.tr = True

	def __str__(self):
		str = `self.p` + '/' + `self.t`
		abilities = []
		if self.ds:
			abilities.append('double strike')
		if self.dt:
			abilities.append('deathtouch')
		if self.f:
			abilities.append('flying')
		if self.fs:
			abilities.append('first strike')
		if self.i:
			abilities.append('indestructible')
		if self.l:
			abilities.append('lifelink')
		if self.m:
			abilities.append('menace')
		if self.r:
			abilities.append('reach')
		if self.tr:
			abilities.append('trample')
		if len(abilities) > 0:
			str += '(' + ', '.join(abilities) + ')'
		return str

	def __repr__(self):
		return str(self)

	def evaluate(self):
		eval = self.p * POWER_EVAL + self.t * TOUGHNESS_EVAL
		if self.ds:
			eval *= DOUBLE_STRIKE_MULT
		if self.dt:
			eval += DEATHTOUCH_EVAL
		if self.f:
			eval += FLYING_EVAL
		if self.fs:
			eval += FIRST_STRIKE_EVAL
		if self.i:
			eval += INDESTRUCTIBLE_EVAL
		if self.l:
			eval += LIFELINK_EVAL
		if self.m:
			eval += MENACE_EVAL
		if self.r:
			eval += REACH_EVAL
		if self.tr:
			eval += TRAMPLE_EVAL
		return eval

def evaluate_creatures(all, dead = []):
	total = (len(all) - len(dead)) * CREATURE_EVAL
	for creature in all:
		if creature not in dead:
			total += creature.evaluate()
	return total

def find_best_attack(life, p1, p2):
	global evaluated_positions
	evaluated_positions = 0
	best_results = {}
	for atx in range(0, pow(2, len(p1))):
		attackers = []
		for i in range(0, len(p1)):
			if get_digit(atx, 2, i):
				attackers.append(i)
		results = find_best_block(life, p1, p2, attackers)
		combine_results(best_results, results, True)
	if evaluated_positions % 100000 != 0:
		print 'Evaluated ' + `evaluated_positions` + ' combats.'
	print 'P1\'s creatures: ' + `p1`
	print 'P2\'s creatures: ' + `p2`
	print 'Opponent is at ' + `life` + ' life. Best attacks according to eval functions:'
	print_results(best_results)

# <attackers> is an array of indices into p1 that represent which of them are attacking.
def find_best_block(life, p1, p2, attackers):
	best_results = {}
	for blx in range(0, pow(len(attackers) + 1, len(p2))):
		legal = True
		# Check for legality of block.
		blockers = [[] for i in range(len(attackers))]
		for i in range(0, len(p2)):
			blk = get_digit(blx, len(attackers) + 1, i)
			if blk == len(attackers):
				continue
			if p1[attackers[blk]].f and not (p2[i].f or p2[i].r):
				# Non-flier/reacher blocking a flier.
				legal = False
				break
			blockers[blk].append(i)
		if not legal:
			continue
		for i in range(0, len(blockers)):
			if len(blockers[i]) == 1 and p1[attackers[i]].m:
				# A menacer is being blocked by a single creature.
				legal = False
				break
		if not legal:
			continue

		results = find_best_ordering(life, p1, p2, attackers, blockers)
		combine_results(best_results, results, False)
	return best_results

def find_best_ordering(life, p1, p2, attackers, blockers):
	best_results = {}
	# Evaluate all possible permutations of the blockers subarrays.
	subpermutations = []
	for array in blockers:
		subpermutations.append(list(itertools.permutations(array)))
	for ordering in itertools.product(*subpermutations):
		results = evaluate_block(life, p1, p2, attackers, ordering)
		combine_results(best_results, results, True)
	return best_results

def evaluate_block(life, p1, p2, attackers, blockers):
	global evaluated_positions
	evaluated_positions += 1
	if evaluated_positions % 10000 == 0:
		print 'Evaluated ' + `evaluated_positions` + ' combats.'
	p1_dead = []
	p2_dead = []
	opponent_fs_damage = 0
	opponent_regular_damage = 0
	for i in range(0, len(attackers)):
		attacking_creature = p1[attackers[i]]
		blocking_creatures = map(lambda x: p2[x], blockers[i])
		blocker_damage = [0] * len(blocking_creatures)
		t = attacking_creature.t

		# First-strike damage between creatures.
		p = attacking_creature.p
		for i in range(0, len(blocking_creatures)):
			blocking_creature = blocking_creatures[i]
			if (attacking_creature.fs or attacking_creature.ds) and p > 0:
				if attacking_creature.dt:
					p -= 1
					if not blocking_creature.i:
						p2_dead.append(blocking_creature)
				else:
					damage = min(p, blocking_creature.t - blocker_damage[i])
					blocker_damage[i] += damage
					if blocker_damage[i] == blocking_creature.t and not blocking_creature.i:
						p2_dead.append(blocking_creature)
					p -= damage
			if blocking_creature.fs or blocking_creature.ds:
				if blocking_creature.l:
					opponent_fs_damage -= blocking_creature.p
				if blocking_creature.dt:
					t = 0
				else:
					t -= blocking_creature.p
		# First-strike damage to players.
		if (attacking_creature.fs or attacking_creature.ds) and \
			 p > 0 and \
			 (len(blocking_creatures) == 0 or attacking_creature.tr):
			opponent_fs_damage += p
		# Check for attacking creature death.
		if t <= 0 and not attacking_creature.i:
			p1_dead.append(attacking_creature)

		# Regular damage.
		p = attacking_creature.p
		if not attacking_creature in p1_dead:
			for i in range(0, len(blocking_creatures)):
				blocking_creature = blocking_creatures[i]
				if blocking_creature in p2_dead:
					continue
				if not attacking_creature.fs and p > 0:
					if attacking_creature.dt:
						p -= 1
						if not blocking_creature.i:
							p2_dead.append(blocking_creature)
					else:
						damage = min(p, blocking_creature.t - blocker_damage[i])
						blocker_damage[i] += damage
						if blocker_damage[i] == blocking_creature.t and not blocking_creature.i:
							p2_dead.append(blocking_creature)
						p -= damage
				if not blocking_creature.fs:
					if blocking_creature.l:
						opponent_regular_damage -= blocking_creature.p
					if blocking_creature.dt:
						t = 0
					else:
						t -= blocking_creature.p
		# Regular damage to players.
		if not attacking_creature.fs and \
			 p > 0 and \
			 (len(blocking_creatures) == 0 or attacking_creature.tr):
			opponent_regular_damage += p
		# Check for attacking creature death.
		if t <= 0 and not attacking_creature.i:
			p1_dead.append(attacking_creature)

	# If we can force a kill against the opponent, go for it.
	opponent_damage = opponent_fs_damage + opponent_regular_damage
	if opponent_fs_damage >= life or opponent_damage >= life:
		opponent_damage_eval = sys.maxint
	else:
		opponent_damage_eval = opponent_damage * LIFE_EVAL * (1 + 1.5 * pow(opponent_damage / float(life), 2))
	# We don't care about opponent lifegain that much.
	if opponent_damage < 0:
		opponent_damage_eval *= .5

	# Only cares about damaging the opponent for a kill or when it comes at no cost to board position.
	board_position = evaluate_creatures(p1, p1_dead) - evaluate_creatures(p2, p2_dead) + opponent_damage_eval * .001
	# Willing to sacrifice some board position to get damage in.
	balanced = evaluate_creatures(p1, p1_dead) - evaluate_creatures(p2, p2_dead) + opponent_damage_eval
	results = {}
	results['board_position'] = Result(p1, p2, attackers, blockers, opponent_damage, board_position)
	results['balanced'] = Result(p1, p2, attackers, blockers, opponent_damage, balanced)
	return results

# opponent's life total
life = 4
# power, toughness, keywords(optional, comma-separated string):
#		ds - double strike
#		dt - deathtouch
#		f - flying
#		fs - first strike
#		i - indestructible
#		l - lifelink
#		m - menace
#		r - reach
#		tr - trample
p1 = [
	Creature(5, 5),
	Creature(5, 5),
	Creature(6, 6, 'tr, m'),
	Creature(5, 5),
	Creature(5, 5),
	Creature(6, 6, 'tr, m'),
]
p2 = [
	Creature(5, 5),
	Creature(3, 1, 'l'),
	Creature(0, 7),
	Creature(5, 5),
	Creature(3, 1, 'l'),
	Creature(0, 7),
]

evaluated_positions = 0
find_best_attack(life, p1, p2)