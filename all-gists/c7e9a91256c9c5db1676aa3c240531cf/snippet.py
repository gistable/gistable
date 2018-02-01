#!/usr/bin/env python

# requires python 3.6 and requests
import os
import re
import secrets
import requests


wordlist_file = 'diceware.wordlist.asc'


if not os.path.isfile(wordlist_file):
    print('Reticulating splines...\n')
    data = requests.get('http://world.std.com/~reinhold/diceware.wordlist.asc').text
    with open(wordlist_file, 'w') as f:
        f.write(data)


random_integer_list = [secrets.choice(range(1, 7)) for i in range(45)]

f = lambda A, n=5: [A[i:i+n] for i in range(0, len(A), n)]

grouped_codes = f(random_integer_list)

passphrase_codes = map(lambda elt: r''.join(str(x) for x in elt), grouped_codes)

passphrase = []

for code in passphrase_codes:
    for line in open(wordlist_file, 'r'):
        if re.match(code, line):
            passphrase.append(line.strip().split('\t')[1])

print(' '.join(passphrase))

# #### download beale.wordlist.asc from http://world.std.com/~reinhold/diceware.html
