#!/usr/bin/python
# authored by Pratul Kalia in January 2011.
# Released into the public domain.

import sys

# Chaldean-Hebrew Kabala Numberical Alphabet.
# Taken from the book "Star Signs" by Linda Goodman.
kabala = {'a': 1, 'b': 2, 'c': 3, 'd': 4,
          'e': 5, 'f': 8, 'g': 3, 'h': 5,
          'i': 1, 'j': 1, 'k': 2, 'l': 3,
          'm': 4, 'n': 5, 'o': 7, 'p': 8,
          'q': 1, 'r': 2, 's': 3, 't': 4,
          'u': 6, 'v': 6, 'w': 6, 'x': 5,
          'y': 1, 'z': 7}

# Do the initial conversion into the sum of numbers.
def kabalize(curr_name):
    sum = 0
    for counter in range(0, len(curr_name)):
        letter = curr_name[counter]
        sum = sum + kabala[letter]

    if (len(str(sum)) > 1):
        squashnumber(sum)
    else:
        print sum

# Keep squashing sum until we get a single digit number
def squashnumber(temp):
    fsum = 0
    fstr = str(temp)
    for counter in range(0, len(fstr)):
        fsum = fsum + int(fstr[counter])

    if (len(str(fsum)) > 1):
        squashnumber(fsum)
    else:
        print fsum

# Let's begin!
for name in sys.argv[1:]:
    print name
    kabalize(name.lower())
