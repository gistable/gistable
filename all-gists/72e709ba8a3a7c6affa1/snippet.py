#!/usr/bin/python
from silk import *
import json
import random
import datetime
import time

def strTimeProp(start, end, format, prop):
    stime = time.mktime(time.strptime(start, format))
    etime = time.mktime(time.strptime(end, format))
    ptime = stime + prop * (etime - stime)
    return time.strftime(format, time.localtime(ptime))


def randomDate(start, end, prop):
    return strTimeProp(start, end, '%Y-%m-%dT%H:%M:%S', prop)

def parse_all():
    ffile = 'flow.rwf'
    flow = SilkFile(ffile,READ)
    i = 5000;
    for rec in flow:
        randDate =randomDate("2014-01-05T16:46:59", "2014-06-05T16:46:59", random.random())
        d = {}
        d['icmpcode'] = rec.icmpcode
        d['sip'] = str(rec.sip)
        d['protocol'] = rec.protocol
        d['output'] = rec.output
        d['packets'] = rec.packets
        d['bytes'] = rec.bytes
        d['application'] = rec.application
        d['sensor_id'] = rec.sensor_id
        d['duration'] = random.randint(0,500)
        d['stime'] = randDate
        d['classtype_id'] = rec.classtype_id
        d['nhip'] = str(rec.nhip)
        d['input'] = rec.input
        d['icmptype'] = rec.icmptype
        d['dip'] = str(rec.dip)
        d['sport'] = rec.sport
        d['dport'] = rec.dport
        print '{"index":{"_index":"netflow","_type":"line","_id":'+str(i)+'}}'
        i +=1
        print json.dumps(d)
print "\n"

   
def main():
    parse_all()

if __name__ == "__main__":
    main()

