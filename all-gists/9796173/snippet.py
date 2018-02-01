#A golfed python 'accent'. Fully backwards compatible with python.
#NOT SUITED FOR DAY-TO-DAY PROGRAMMING!
#If you DO use it for a production (non-challenge/codegolf) program, I'm not
#responsible for anything bad that happens to you, your computer,
#your spare time, your code maintainability, any kittens that god might kill,
#or the tears of blood you will weep.

import sys

from math import *


Al=all
An=any

import collections
C=collections
CC = C.Counter
CD = C.deque
Cd = C.defaultdict
Cn = C.namedtuple
CO = C.OrderedDict


D=None
E=eval
F=None
G=None
H=None

I=__import__
Ip=input

import itertools
It=itertools

ItCo = It.count
ItCy = It.cycle
ItRe = It.repeat

ItCh = It.chain
ItCo = It.compress
ItDW = It.dropwhile
ItGB = It.groupby
ItiF = It.ifilter
ItiS = It.islice
ItiM = It.imap
ItSM = It.starmap
Itt  = It.tee
ItTW = It.takewhile
ItiZ = It.izip
ItiZL= It.izip_longest

ItPr = It.product
ItPe = It.permutations
ItCo = It.combinations
ItCoR= It.combinations_with_replacement


def J(iterable):
    return "".join(iterable)


K=1000
L=list
M=map
Mx=max
Mn=min
N="\n"
O=None

def P(*args):
    for arg in args:
        print arg
#Print expand
def Pe(*args):
    for arg in args:
        print
        for subarg in arg:
            print subarg,

#Print joined
def PJ(*args):
    
    print J(args)
            

Q=None #Quine, this is defined later on.


R=range

import random
Ra=random
#Probably not neccesary, but hey :)
RaSe  = Ra.seed
RaGS = Ra.getstate
RaSS = Ra.setstate
RaJA = Ra.jumpahead
RaRB = Ra.getrandbits
#The interesting part:
RR  = Ra.randrange
RI  = Ra.randint
RS  = Ra.shuffle
RSm = Ra.sample
RR  = Ra.random
RU  = Ra.uniform
RT  = Ra.triangular
RBv = Ra.betavariate
REv = Ra.expovariate
RGv = Ra.gammavariate
RG  = Ra.gauss
RLv = Ra.lognormvariate
RNv = Ra.normalvariate
RVv = Ra.vonmisesvariate
RPv = random.paretvariate
RWv = random.weibullvariate



import re
Re=re
#TODO: Add short notations

S=sorted
Se=set
Sp=" "

import string
ST=string
STl  = string.ascii_letters
STlc = string.ascii_lowercase
STuc = string.ascii_uppercase
STd  = string.digits
STod = string.octdigits
STp  = string.punctuation
STP  = string.printable
STw  = string.whitespace


try:
    STDI = sys.stdin
except AttributeError:
    STDI = None
    
T=tuple
U=None
V=None
W=None
X=range
Y=None
Z=zip

if len(sys.argv)==1:
    print "Usage: python",sys.argv[0],"[filename]"
else:
    fle=open(sys.argv[1])
    code=Q=fle.read()
    #Q stands for quine. P(Q) works.
    #Working on this \|/
    """
    #This will attempt to close your parrens. DO CLOSE YOUR STRINGS!
    parrens={"(":")","{":"}","[":"]"}
    reqparrens=" "
    for char in code:
        if char in parrens:
            reqparrens=parrens[char]+reqparrens
        elif char == reqparrens[0]:
    """
    exec(code)
    fle.close()
