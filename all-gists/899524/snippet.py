# Adapted from http://j2labs.tumblr.com/post/4262756632/speed-tests-for-json-and-cpickle-in-python

import time
import cPickle as pickle
import simplejson
import json
import cjson
import jsonlib
import ujson


cjson.dumps = cjson.encode
cjson.loads = cjson.decode


def test_mod(mod, iters=1000000):
    d = {
        'foo': 'bar',
        'food': 'barf',
        'good': 'bars',
        'dood': 'wheres your car?',
        'wheres your car': 'dude?',
    }

    print 'Starting %s...' % mod.__name__
    start = time.time()
    for i in xrange(iters):
        s = mod.dumps(d)
    write = time.time() - start

    start = time.time()
    for i in xrange(iters):
        dl = mod.loads(s)
    read = time.time() - start

    print 'Read: %f, Write: %f, Total %f' % (read, write, read + write)

to_test = [cjson, ujson, json, simplejson, pickle, jsonlib]
for mod in to_test:
    test_mod(mod)
