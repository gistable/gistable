#!/usr/bin/env python
from collections import defaultdict
from random import choice, randint
from re import findall

# Make sure that this will run in python 2 as well as 3
try:
	input = raw_input
except NameError:
	pass

text = open(input('File to train on: ')).read()
order = int(input('Order: '))
output_length = int(input('Output Length: '))

words = findall("[a-z']+", text.lower())
states = defaultdict(list)

for i in range(len(words) - order):
    states[tuple(words[i:i + order])].append(words[i + order])

start_seed = randint(0, len(words) - order)
terms = words[start_seed:start_seed + order]

for _ in range(output_length):
    terms.append(choice(states[tuple(terms[-order:])]))

print(' '.join(terms))