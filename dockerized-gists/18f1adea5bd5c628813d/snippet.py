#! /usr/bin/env python

import numpy.random as npr

SIZE=3030
LOOPS=1000000

TIE=SIZE/2

ties=0
for i in range(1, LOOPS):
    a = npr.randint(2, size=SIZE)
    if sum(a) == TIE:
        ties += 1
    if i % 1000 == 0:
        print("Total: {} ties: {} prob: {}".format(i, ties, ties/float(i)))