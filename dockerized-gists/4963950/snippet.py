#!/usr/bin/env python -tt
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import os, os.path
import sys
import re
from pprint import pprint, pformat

import json
import msgpack

import timeit

'''
RESULTS:
json encode (small): 0.0951790809631
msgpack encode (small): 0.0478010177612
json encode (medium): 0.532800197601
msgpack encode (medium): 0.120756149292
json encode (big): 13.5378389359
msgpack encode (big): 3.8050031662
json decode (small): 0.101329088211
msgpack decode (small): 0.0355620384216
json decode (medium): 0.603298187256
msgpack decode (medium): 0.0926129817963
json decode (big): 20.697480917
msgpack decode (big): 2.18435788155
(tmsgpack)[mysz@McMySZ ~/Projects/tmsgpack]%
'''

SS = {
    'a': 1,
    'b': 2,
}
def tjson_e_s ():
    return json.dumps (SS)

def tmsgpack_e_s ():
    return msgpack.packb (SS)

SM = {}
for i in range (10):
    k = chr (i+70)
    SM[k] = [ j for j in range (20) ]
# print (SM)
# sys.exit ()

def tjson_e_m ():
    return json.dumps (SM)

def tmsgpack_e_m ():
    return msgpack.packb (SM)

SB = {}
for i in range (40):
    k = chr (i+60)
    SB[k] = [ [ k for k in range (100) ] for j in range (100) ]

# print (SB)
# sys.exit ()

def tjson_e_b ():
    return json.dumps (SB)

def tmsgpack_e_b ():
    return msgpack.packb (SB)


print ('json encode (small):', timeit.timeit (tjson_e_s, number=10000))
print ('msgpack encode (small):', timeit.timeit (tmsgpack_e_s, number=10000))

print ('json encode (medium):', timeit.timeit (tjson_e_m, number=10000))
print ('msgpack encode (medium):', timeit.timeit (tmsgpack_e_m, number=10000))

print ('json encode (big):', timeit.timeit (tjson_e_b, number=10000))
print ('msgpack encode (big):', timeit.timeit (tmsgpack_e_b, number=10000))

SSJ = json.dumps (SS)
def tjson_d_s ():
    return json.loads (SSJ)

SSM = msgpack.packb (SS)
def tmsgpack_d_s ():
    return msgpack.unpackb (SSM)

SMJ = json.dumps (SM)
def tjson_d_m ():
    return json.loads (SMJ)

SMM = msgpack.packb (SM)
def tmsgpack_d_m ():
    return msgpack.unpackb (SMM)

SBJ = json.dumps (SB)
def tjson_d_b ():
    return json.loads (SBJ)

SBM = msgpack.packb (SB)
def tmsgpack_d_b ():
    return msgpack.unpackb (SBM)

print ('json decode (small):', timeit.timeit (tjson_d_s, number=10000))
print ('msgpack decode (small):', timeit.timeit (tmsgpack_d_s, number=10000))

print ('json decode (medium):', timeit.timeit (tjson_d_m, number=10000))
print ('msgpack decode (medium):', timeit.timeit (tmsgpack_d_m, number=10000))

print ('json decode (big):', timeit.timeit (tjson_d_b, number=10000))
print ('msgpack decode (big):', timeit.timeit (tmsgpack_d_b, number=10000))
