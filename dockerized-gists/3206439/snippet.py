#!/usr/bin/env python
"""
Calculate the points for running on Fitocracy
"""
mile = 1.609344

def basepoints(d,p):
    d/=mile
    p*=mile
    return (0.000555476190476192 * p**2 - 0.8333 * p + 382) \
        * 1.0011 * d**0.2012 * d
    # formula from http://fellrnr.com/wiki/Fitocracy

def terrain(x):
    weights = [1.0, 1.115, 1.266, 1.393, 1.532]
    return weights[x]

if __name__ == '__main__':
    d = float(raw_input('distance: '))
    p = map(float,raw_input('pace or time: ').split(':'))
    p = p[0]*60 + p[1]
    if p > 600: # when pace is >10min/km assume it's total time
        p/=d
    t = int(raw_input('terrain [0]: ') or 0)

    print basepoints(d,p) * terrain(t)
