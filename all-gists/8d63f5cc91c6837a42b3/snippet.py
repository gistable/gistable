#!/usr/bin/python
####################                            ####################
#                                                                  #
# Written by Ole Aass (2015)                                       #
# Inspired by Metasploit's pattern_(create|offset).rb              #
#                                                                  #
####################                            ####################

import sys

def offset(eip, pattern, endian):
    eip = eip.decode('hex');
    eip = eip[::-1] if endian is 'little' else eip
    if pattern is None:
        pattern = create(10000)
    return pattern.index(eip)

def create(length):
    uppermap = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lowermap = "abcdefghijklmnopqrstuvwxyz"
    digitmap = "0123456789"

    pattern = ''
    x = y = z = 0

    while True:
        if len(pattern) < length:
            pattern += uppermap[x]
        if len(pattern) < length:
            pattern += lowermap[y]
        if len(pattern) < length:
            pattern += digitmap[z]
        if len(pattern) >= length:
            break

        z += 1
        if x is 25:
            x = 0
        if y is 25:
            y = 0
            x += 1
        if z is 10:
            z = 0
            y += 1


    return pattern

if sys.argv[1] == '-c':
    try:
        length = int(sys.argv[2])
        print create(length)
    except:
        print 'Usage: %s -c <int:length>'%(sys.argv[0])
elif '-o' in sys.argv[1]:
    try:
        eip = sys.argv[2]
        pattern = None if not len(sys.argv) is 4 else sys.argv[3]
        endian = 'big' if sys.argv[1] == '-ob' else 'little'
        offset = offset(eip, pattern, endian)
        print '[+] Offset found at %d bytes'%(offset)
    except ValueError:
        print '[-] Unable to locate offset.'
    except:
        print 'Usage: %s <-ol|-ob> <eip> [pattern]'%(sys.argv[0])
elif sys.argv[1] == '-h':
    print """
####################                            ####################
#                                                                  #
# Written by Ole Aass (2015)                                       #
# Inspired by Metasploit's pattern_(create|offset).rb              #
#                                                                  #
####################                            ####################
    
Switches:
-c <int:length>    Create pattern
-ol|-ob <eip>      l = little, b = big endian

Usage examples:
Create pattern
python pattern.py -c 250       Creates a 250 bytes long pattern

Find offset at which a match was found
python pattern.py -ol 63413563
python pattern.py -ol 63413563 Pattern

"""