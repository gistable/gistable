# This requires pywhois - https://github.com/unpluggd/pywhois/tree/master/pywhois

import pywhois
from itertools import product
from string import ascii_lowercase

length = 3

domains = [''.join(i) for i in product(ascii_lowercase, repeat = length)]

print 'Available:'

for d in domains:
    if not pywhois.whois(d+'.io'):
        print d + ".io is available

print 'Done!'
