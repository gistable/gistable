# This script is released 'as is' into the public domain
from math import cos,sin
import os
from time import sleep
def y(p):
    return (sin(p)**3)
def x(p):
    return -(13*cos(p)-5*cos(2*p)-2*cos(3*p)-cos(4*t))/16
while True:
    for r in range(14):
        os.system('clear')
        c = [[' ' for n in range(30)] for m in range(30)]
        for t in range(100*r):
            p = 0.0628/r*t
            c[int(r*x(p)+15)][int(r*y(p)+15)] = '#'
        for n in c:
            print ''.join(n)
        sleep(0.1)
    sleep(1)
    msg = 'Alice and Bob'.split(' ')
    for n in range(3):
        os.system('clear')
        for m,a in enumerate(msg[n]):
            c[14+2*n][15+m-len(msg[n])/2]=a
        for n in c:
            print ''.join(n)
        sleep(0.4)
    sleep(2)