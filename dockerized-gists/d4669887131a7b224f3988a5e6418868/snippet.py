#!/usr/bin/python

# You have 17 red and 17 blue balls, and you remove two at a time. If
# the two are the same colour, add in one extra blue ball. If they are
# different colours, add in an extra red ball. What colour is the
# final ball removed?

import random

pit = ['blue']*17 + ['red']*17

verbose = False

while len(pit) > 1:
    if verbose:
        print pit

    first  = pit.pop(random.randint(0, len(pit)-1))
    second = pit.pop(random.randint(0, len(pit)-1))

    if first == second:
        add = 'blue'
    else:
        add = 'red'

    if verbose:
        print "Pulled " + first + ", " + second + " so adding " + add

    pit.append(add)

print pit[0]
