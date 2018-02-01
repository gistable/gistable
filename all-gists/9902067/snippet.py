# Perhaps read this first: http://steamcommunity.com/app/266010/discussions/0/558750717604246010/

from __future__ import print_function # Python 2 compatibility
from itertools import cycle
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen # Python 2 compatibility


items = []

resp = urlopen('http://blaxpirit.pythonanywhere.com/lyne/text')  # Get the contents from this URL
for line in resp:  # Go over each line
    line = line.strip().decode()  # Remove any extra spaces at the ends and decode it from bytes to text
    number, letter, a, b = line.split()  # Get the 4 space-separated parts
    number = int(number)  # (number should be an integer)
    items.append((number, letter, a, b))  # Add them to the list of items
resp.close()  # Close the connection
# `items` looks like this now:
# [(1, 'a', '10011010011', '00001000000100101100'), (2, 'a', '01010000010', '10001000001000100000'), ...]

# These codes (bit orderings) are based on the X and Y entries
# http://blaxpirit.pythonanywhere.com/lyne/information
code_a = [  # 2x3
    2**3,                    #  -
    2**0, None, 2**2, 2**6,  # |\/|
    2**8,                    #  -
    2**4, 2**5, None, 2**7,  # |\/|
    2**1,                    #  -
]
code_b = [  # 3x3
    2**1, 2**11,                                  #  -  -
    2**13, None, 2**7, 2**12, 2**5, None, 2**10,  # |\/|\/|
    2**15, 2**3,                                  #  -  -
    2**9, 2**4, None, 2**2, None, 2**6, 2**0,     # |\/|\/|
    2**8, 2**14                                   #  -  -
]


def decode(word, code):
    # http://docs.python.org/library/functions.html#zip
    # Goes over the submitted sequence of bits together with the code
    # and returns the sum of multiplying them together (need to skip the unused None parts too)
    # (bit may need to be converted from a character to integer because words are stored as strings)
    return sum(int(bit)*m for bit, m in zip(word, code) if m is not None)

# The mapping (dictionary) from the numbers the 3x3s give to numbers the 2x3s give
ordered = {}
for number, letter, a, b in items:  # Go over the 4 parts of each of the items:
    if letter=='a':  # if it's an A item,
        ordered[decode(b, code_b)] = decode(a, code_a)  # decoded 3x3 will map to the decoded 2x3
# `ordered` looks like this now:
# {0: 188, 1: 150, 2: 217, 3: 133, 4: 218, 5: 232, 6: 231, ...}


max_n = max(ordered.keys())  # The maximal number (from 3x3s) should be 983

key = 'solelyspace'  # The key decoded from solving the Z part of the puzzle
# The numbers from 2x3s are the result of http://en.wikipedia.org/wiki/Vigenere_cipher

# http://docs.python.org/library/itertools.html#itertools.cycle
# http://docs.python.org/library/functions.html#range
# http://simple.wikipedia.org/wiki/ASCII
# Go over the key repeated over and over together with numbers 0, 1, ... max_n
for i, k in zip(range(max_n+1), cycle(key)):
    try:  # Try to...
        # Print the ASCII/Unicode character at the position that equals ordered[i] minus
        # the position of the next character of the cycled key in ASCII table
        # (ordered[i] is the number from decoding a 2x3)
        print(chr(ordered[i]-ord(k)), end='')
    except: # If some error happens
        # (this can mean a bad or missing entry in the database; "ordered" is not completely filled)
        print('*', end='') # Just print a star placeholder
print()

try:
    input("Press Enter...")
except:
    pass