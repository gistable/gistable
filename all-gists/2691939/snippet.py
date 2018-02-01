#!/usr/bin/env python

#
# Script to poll Ethernet interface counters from a SNMP host
# requires pysnmp and the handy snmpclient library from
# https://github.com/seveas/python-snmpclient
#
# licensed under creative commons CC0 (public domain)
#

import sys
import time
import sched

import snmpclient
import pysnmp.entity.rfc3413.oneliner.cmdgen as cmdgen

client = snmpclient.SnmpClient('192.168.1.10', [{}])
generator = cmdgen.CommandGenerator()
target = cmdgen.UdpTransportTarget((client.host, client.port))

oids = ['IF-MIB::ifHCInOctets.10001', 'IF-MIB::ifHCOutOctets.10002', 'IF-MIB::ifHCOutOctets.10003']
noids = map(snmpclient.nodeid, oids)

s = sched.scheduler(time.time, time.sleep)

with file(sys.argv[1], 'a') as f:
    f.write('# start\n')

    def poll(sc):
        s.enter(1, 1, poll, (s,))
        val = [time.time()]
        for noid in noids:
            error, _, _, binds = generator.getCmd(client.auth, target, noid)
            if error:
                raise Exception('FAIL')
            val.append(int(binds[0][1]))

        val = ','.join(map(str, val))
        f.write(val)
        f.write('\n')
        f.flush()
        print val

    s.enter(1, 1, poll, (s,))
    s.run()