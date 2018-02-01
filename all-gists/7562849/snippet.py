# -*- coding: utf-8 -*-
import sys
import os, os.path
os.chdir(os.path.dirname(os.path.realpath(__file__))
if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

from datetime import datetime


def readf(fname):
    recs = []
    for line in open(fname, 'rb'):
        pics = [w.strip() for w in line.strip().split("\t")]
        if len(pics) == 3:
            pics[1] = datetime.strptime(pics[1], '%Y-%m-%d %H:%M:%S')
            recs.append(pics)
    return recs


def compute(recs, seconds=180):
    ws = []
    ips = {}
    for r in recs:
        last = ips.get(r[2])
        ips[r[2]] = r[1]
        if not last:
            ws.append([r[0]])
        elif (r[1]-last).seconds > seconds:
            ws.append([r[0]])
        else:
            ws[-1].append(r[0])
    vs = ["".join(w) for w in ws]
    return vs


def count(vs):
    m = 0
    n = 0
    for v in vs:
        if v.startswith('ABB'):
                m += 1
                if 'C' in v:
                        n += 1
    return (m, n)



if __name__ == '__main__':
    fname = 'res.txt'
    m, n = count(compute(readf(fname)))
    print m, n
    print "%.1f%%" % (100 - n * 100.0 / m)