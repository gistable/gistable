#!/usr/bin/env python
#
# markov.py
# Generates a Markov chain from a body of text.
#

from __future__ import print_function

import sys
import random
import re

END_CHANCE = 40

def nwise(it, n):
	prior = []
	for element in it:
		yield element, tuple(prior)
		prior.append(element)
		if len(prior) > n:
			prior.pop(0)

# Check that we have an argument.
if len(sys.argv) < 3:
	print('USAGE: {} <text file> <N>'.format(sys.argv[0]), file=sys.stderr)
	sys.exit(1)

filename, N = sys.argv[1], int(sys.argv[2])

probabilities = {}

for word, prior in nwise(filter(lambda x: x, re.split(r"'?[^a-zA-Z0-9'\.-]'?", ''.join(open(sys.argv[1], 'r').readlines()))), N):
	if prior not in probabilities:
		probabilities[prior] = {}
	if word not in probabilities[prior]:
		probabilities[prior][word] = 0
	probabilities[prior][word] += 1

word = random.choice([t for t in probabilities if t and t[0][0] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'])

while True:
	if word and word[0][-1] == '.' and random.randint(0, 99) < END_CHANCE:
		print(word[0])
		break
	print(word[0], end= ' ')
	word = word[1:] + (random.choice(reduce(lambda a, b: a + b, [[key] * value for key, value in probabilities[word].iteritems()])),)
