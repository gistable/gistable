#!/usr/bin/env python

# Now you'll be able to read those encoded/compressed 
# responses in your vcrpy test artifacts!
# References:
# https://github.com/kevin1024/vcrpy/issues/249
# http://stackoverflow.com/questions/36366234
# Thanks to Reti43 on StackOverflow

import sys
import yaml

# decode_response doesn't exist in vcrpy 1.7.4 from pypi!
# pip install from source instead
from vcr.filters import decode_response

if len(sys.argv) not in [2, 3]:
    print "Usage: decode_vcrpy.py path/to/fixture.yaml [response number, ex '0']"
    sys.exit(1)

with open(sys.argv[1], 'r') as f:
    doc = yaml.load(f)

if len(sys.argv) == 3:
    response = doc['interactions'][int(sys.argv[2])]['response']
    print(decode_response(response)['body']['string'])
    sys.exit(0)

for index, interaction in enumerate(doc['interactions']):
    print('################')
    print('response %d'%index)
    print('uri: %s'%interaction['request']['uri'])
    print('response:')

    decoded = decode_response(interaction['response'])
    print(decoded['body']['string'])