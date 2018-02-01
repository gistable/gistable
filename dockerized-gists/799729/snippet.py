#!/usr/bin/env python

from random import random, randint, choice
from copy import deepcopy
from math import log

TAB = "  "

### classes ##

class func:
    def __init__(self, fn, argn, name):
        self.fn = fn
        self.argn = argn
        self.name = name

class node:
    def __init__(self, func, children):
        self.func = func
        self.children = children

        self.fn = func.fn
        self.name = func.name

    def evaluate(self, inp):
        results = [n.evaluate(inp) for n in self.children]
        return self.fn(results)

    def display(self, indent=0):
        print (TAB*indent)+self.name
        for c in self.children:
            c.display(indent+1)

class var:
    def __init__(self, idx):
        self.idx = idx

    def evaluate(self, inp):
        return inp[self.idx]

    def display(self, indent=0):
        print (TAB*indent)+"x"+str(self.idx)

class const:
    def __init__(self, c):
        self.c = c

    def evaluate(self, inp):
        return self.c

    def display(self, indent=0):
        print (TAB*indent)+str(self.c)

### func definitions ###

addf = func(lambda x: x[0]+x[1], 2, "add")
subf = func(lambda x: x[0]-x[1], 2, "subtract")
mulf = func(lambda x: x[0]*x[1], 2, "multiply")
#divf = func(lambda x: float(x[0])/float(x[1]), 2, "divide")
#intdivf = func(lambda x: x[0]/x[1], 2, "intdiv")
#expf = func(lambda x: x[0] ** x[1], 2, "exponent")

def iffunc(x):
    if x[0] > 0:
        return x[1]
    else:
        return x[2]
iff = func(iffunc, 3, 'if')

def isgreater(x):
    if x[0] > x[1]:
        return 1
    else:
        return 0
isgreaterf = func(isgreater, 2, "isgreater")

def isless(x):
    if x[0] < x[1]:
        return 1
    else:
        return 0
islessf = func(isless, 2, "isless")

def isequal(x):
    if x[0] == x[1]:
        return 1
    else:
        return 0
isequalf = func(isequal, 2, "isequal")

funclist = [addf, subf, mulf, isgreaterf, islessf, isequalf]

### genetics ###

def makerandomtree(argn, maxdepth=4, fpr=0.7, vpr = 0.6):
    if random() < fpr and maxdepth > 0:
        f = choice(funclist)
        children = [makerandomtree(argn, maxdepth-1, fpr, vpr)
                    for i in range(f.argn)]
        return node(f, children)
    elif random () < vpr:
        return var(randint(0, argn-1))
    else:
        return const(randint(0, 10))

def score(tree, s):
    dif = 0
    for data in s:
        v = tree.evaluate([data[0], data[1]])
        dif += abs(v-data[2])
    return dif

def mutate(t, argn, pchg=0.1):
    if random() < pchg:
        return makerandomtree(argn)
    else:
        result = deepcopy(t)
        if isinstance(t, node):
            result.children = [mutate(c, argn, pchg) for c in t.children]
        return result

def crossover(t1, t2, pswp=0.7, top=1):
    if random()<pswp and not top:
        return deepcopy(t2)
    else:
        result = deepcopy(t1)
        if isinstance(t1, node) and isinstance(t2, node):
            result.children = [crossover(c, choice(t2.children), pswp, 0)
                               for c in t1.children]
        return result

def evolve(argn, psize, rankf, maxgen=500,
           mutrate=0.1, breedrate=0.4, pexp=0.7, pnew=0.05):
    def selectindex():
        return int(log(random())/log(pexp))

    population = [makerandomtree(argn) for i in range(psize)]
    for i in range(maxgen):
        scores = rankf(population)
        print scores[0][0]
        if scores[0][0] == 0:
            break

        newpop = [scores[0][1], scores[1][1]]
        while(len(newpop)<psize):
            if random() < pnew:
                newpop.append(mutate(
                    crossover( scores[selectindex()][1],
                               scores[selectindex()][1],
                               pswp=breedrate ),
                    argn, pchg=mutrate))
            else:
                newpop.append(makerandomtree(argn))
        population = newpop
    scores[0][1].display()
    return scores[0][1]

def getrankf(dataset):
    def rankf(population):
        scores=[(score(t, dataset), t) for t in population]
        scores.sort()
        return scores
    return rankf

### testing ###

if __name__ == "__main__":
    def mystery(x, y):
        return x**2+2*y+3*x+5

    def buildset():
        rows = []
        for i in range(200):
            x = randint(0, 40)
            y = randint(0, 40)
            rows.append([x, y, mystery(x, y)])
        return rows

    rf = getrankf(buildset())
    evolve(2, 500, rf, mutrate=0.2, breedrate=0.1, pexp = 0.7, pnew=0.1)
