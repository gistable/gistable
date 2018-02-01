#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import binascii
import md5

def search(nodelist, key):
    max_len = len(nodelist)
    keys = sorted( nodelist.keys() )
    for i , nodekey in enumerate(keys):
        if   keys[i-1] <  key <= keys[i]:
            return nodelist[keys[i]]
    return nodelist[keys[0]]

number_of_node = 128
crc = binascii.crc32
hash = md5.new()

node = ["n1","n2", "n3", "n4","n5", "n6", "n7"]
circle = {}

for no in node:
    for i in range(number_of_node):
        hash.update(no + '_%d' % i)
        circle[hash.hexdigest()]  = no
#print circle

for s in range(ord('A'), ord('Z')):
    store = crc(chr(s)) % len(node)
    #print chr(s), " : ", store
    #print store , " : " , chr(s)
    print chr(s) , " : ",
    hash.update(chr(s))
    print search(circle, hash.hexdigest() )


# http://8-p.info/consistent-hashing/