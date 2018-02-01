#!/usr/bin/env python

# The output geneally looks like this:
#
#    $ ./serialization.py
#    Dumping:
#      json: 6.40960884094
#      simplejson: 6.82945179939
#      cjson: 2.23045802116
#      ujson: 0.806604146957
#      cPickle: 6.72593593597
#    Loading:
#      json: 8.34801983833
#      simplejson: 3.70781588554
#      cjson: 1.73801183701
#      ujson: 1.10599803925
#      cPickle: 3.06558394432
#

import time

import cPickle
import simplejson
import json
import cjson # python-cjson in pypi
import ujson

### Make cjson's interface match the others
cjson.dumps = cjson.encode
cjson.loads = cjson.decode

### Prepare data structures
data_as_dict = {
    'foo': 'bar',
    'food': 'barf',
    'good': 'bars',
    'dood': 'wheres your car?',
    'wheres your car': 'dude?',
}
data_as_json = json.dumps(data_as_dict)
data_as_pickled = cPickle.dumps(data_as_dict)

### 
num_loop_iterations = 1000000

### List of JSON implementations to test
mods = [json, simplejson, cjson, ujson, cPickle]


### Time dumping from native to JSON
print 'Dumping:'
for mod in mods:
    start = time.time()
    for i in xrange(num_loop_iterations):
        mod.dumps(data_as_dict)
    print '  %s: %s' % (mod.__name__, (time.time() - start))


### Time loading from JSON into native
print 'Loading:'
for mod in mods:
    data = data_as_json
    if mod.__name__ == "cPickle":
        data = data_as_pickled
        
    start = time.time()
    for i in xrange(num_loop_iterations):
        mod.loads(data)
    print '  %s: %s' % (mod.__name__, (time.time() - start))
