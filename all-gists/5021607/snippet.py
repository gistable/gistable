#!/usr/bin/env python

import copy


f = open('weechat.conf', 'r')

formats = ['/join ', '/query ']

networks = {
        'freenode': copy.copy(formats),
        'oftc': copy.copy(formats),
        'efnet': copy.copy(formats),
        }

for line in f:
    for network in networks.keys():
        if 'buffer = "irc;' + network in line:
            l = line.split(';')
            g = l[1].split('.', 1)
            channel = ''.join(g[1:])
            if channel.startswith('#'):
                networks[network][0] += channel + ','
            else:
                nick = channel
                networks[network][1] += nick + '; '

f.close()

for x in networks:
    print x
    for y in networks[x]:
        print '\t', y
    print ''