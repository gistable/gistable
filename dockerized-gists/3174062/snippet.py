"""
Dependencies:

    pip install tabulate simplejson python-cjson ujson yajl msgpack-python

"""

from timeit import timeit 
from tabulate import tabulate

setup = '''d = {
    'words': """
        Lorem ipsum dolor sit amet, consectetur adipiscing 
        elit. Mauris adipiscing adipiscing placerat. 
        Vestibulum augue augue, 
        pellentesque quis sollicitudin id, adipiscing.
        """,
    'list': range(100),
    'dict': dict((str(i),'a') for i in xrange(100)),
    'int': 100,
    'float': 100.123456
}'''

setup_pickle    = '%s ; import cPickle ; src = cPickle.dumps(d)' % setup
setup_pickle2   = '%s ; import cPickle ; src = cPickle.dumps(d, 2)' % setup
setup_json      = '%s ; import json; src = json.dumps(d)' % setup
setup_msgpack   = '%s ; src = msgpack.dumps(d)' % setup

tests = [
    # (title, setup, enc_test, dec_test)
    ('pickle (ascii)', 'import pickle; %s' % setup_pickle, 'pickle.dumps(d, 0)', 'pickle.loads(src)'),
    ('pickle (binary)', 'import pickle; %s' % setup_pickle2, 'pickle.dumps(d, 2)', 'pickle.loads(src)'),
    ('cPickle (ascii)', 'import cPickle; %s' % setup_pickle, 'cPickle.dumps(d, 0)', 'cPickle.loads(src)'),
    ('cPickle (binary)', 'import cPickle; %s' % setup_pickle2, 'cPickle.dumps(d, 2)', 'cPickle.loads(src)'),
    ('json', 'import json; %s' % setup_json, 'json.dumps(d)', 'json.loads(src)'),
    ('simplejson-3.3.1', 'import simplejson; %s' % setup_json, 'simplejson.dumps(d)', 'simplejson.loads(src)'),
    ('python-cjson-1.0.5', 'import cjson; %s' % setup_json, 'cjson.encode(d)', 'cjson.decode(src)'),
    ('ujson-1.33', 'import ujson; %s' % setup_json, 'ujson.dumps(d)', 'ujson.loads(src)'),
    ('yajl 0.3.5', 'import yajl; %s' % setup_json, 'yajl.dumps(d)', 'yajl.loads(src)'),
    ('msgpack-python-0.3.0', 'import msgpack; %s' % setup_msgpack, 'msgpack.dumps(d)', 'msgpack.loads(src)'),
]

loops = 15000
enc_table = []
dec_table = []

print "Running tests (%d loops each)" % loops

for title, mod, enc, dec in tests:
    print title

    print "  [Encode]", enc 
    result = timeit(enc, mod, number=loops)
    enc_table.append([title, result])

    print "  [Decode]", dec 
    result = timeit(dec, mod, number=loops)
    dec_table.append([title, result])

enc_table.sort(key=lambda x: x[1])
enc_table.insert(0, ['Package', 'Seconds'])

dec_table.sort(key=lambda x: x[1])
dec_table.insert(0, ['Package', 'Seconds'])

print "\nEncoding Test (%d loops)" % loops
print tabulate(enc_table, headers="firstrow")

print "\nDecoding Test (%d loops)" % loops
print tabulate(dec_table, headers="firstrow")

"""
OUTPUT:

Running tests (15000 loops each)
pickle (ascii)
  [Encode] pickle.dumps(d, 0)
  [Decode] pickle.loads(src)
pickle (binary)
  [Encode] pickle.dumps(d, 2)
  [Decode] pickle.loads(src)
cPickle (ascii)
  [Encode] cPickle.dumps(d, 0)
  [Decode] cPickle.loads(src)
cPickle (binary)
  [Encode] cPickle.dumps(d, 2)
  [Decode] cPickle.loads(src)
json
  [Encode] json.dumps(d)
  [Decode] json.loads(src)
simplejson-3.3.1
  [Encode] simplejson.dumps(d)
  [Decode] simplejson.loads(src)
python-cjson-1.0.5
  [Encode] cjson.encode(d)
  [Decode] cjson.decode(src)
ujson-1.33
  [Encode] ujson.dumps(d)
  [Decode] ujson.loads(src)
yajl 0.3.5
  [Encode] yajl.dumps(d)
  [Decode] yajl.loads(src)
msgpack-python-0.3.0
  [Encode] msgpack.dumps(d)
  [Decode] msgpack.loads(src)

Encoding Test (15000 loops)
Package                 Seconds
--------------------  ---------
ujson-1.33             0.232215
msgpack-python-0.3.0   0.241945
cPickle (binary)       0.305273
yajl 0.3.5             0.634148
python-cjson-1.0.5     0.680604
json                   0.780438
simplejson-3.3.1       1.04763
cPickle (ascii)        1.62062
pickle (ascii)        14.0497
pickle (binary)       15.4712

Decoding Test (15000 loops)
Package                 Seconds
--------------------  ---------
msgpack-python-0.3.0   0.240885
cPickle (binary)       0.393152
ujson-1.33             0.396875
python-cjson-1.0.5     0.694321
yajl 0.3.5             0.748369
simplejson-3.3.1       0.780531
cPickle (ascii)        1.38561
json                   1.65921
pickle (binary)        5.20554
pickle (ascii)        17.8767
"""