#!/usr/bin/env python

from collections import OrderedDict
import json

write_data = OrderedDict([
    ('a', '1'),
    ('b', '2'),
    ('c', '3')
])

print 'It\'s a dict!'
print write_data
print ''

with open('test.json', 'w') as f:
    json.dump(write_data, f)

with open('test.json') as f:
    read_data = json.load(f)

print 'Order is not guaranteed:'
print read_data
print ''

with open('test.json') as f:
    read_data = json.load(f, object_pairs_hook=OrderedDict)

print 'Order *is* guaranteed:'
print read_data