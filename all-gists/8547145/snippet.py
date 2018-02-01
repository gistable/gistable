from collections import OrderedDict
import itertools
from random import shuffle, randint
import re
from sets import Set

def f1(seq): # Raymond Hettinger
    # not order preserving
    set = {}
    map(set.__setitem__, seq, [])
    return set.keys()

def f2(seq):   # *********
    # order preserving
    checked = []
    for e in seq:
        if e not in checked:
            checked.append(e)
    return checked

def f3(seq):
    # Not order preserving
    keys = {}
    for e in seq:
        keys[e] = 1
    return keys.keys()

def f4(seq): # ********** order preserving
    noDupes = []
    [noDupes.append(i) for i in seq if not noDupes.count(i)]
    return noDupes

def f5(seq, idfun=None): # Alex Martelli ******* order preserving
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result

def f5b(seq, idfun=None): # Alex Martelli ******* order preserving
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker not in seen:
            seen[marker] = 1
            result.append(item)
            
    return result



def f6(seq):
    # Not order preserving
    return list(Set(seq))

def f7(seq):
    # Not order preserving
    return list(set(seq))

def f8(seq): # Dave Kirby
    # Order preserving
    seen = set()
    return [x for x in seq if x not in seen and not seen.add(x)]

def f9(seq):
    # Not order preserving
    return {}.fromkeys(seq).keys()

def f10(seq, idfun=None): # Andrew Dalke
    # Order preserving
    return list(_f10(seq, idfun))

def _f10(seq, idfun=None):
    seen = set()
    if idfun is None:
        for x in seq:
            if x in seen:
                continue
            seen.add(x)
            yield x
    else:
        for x in seq:
            x = idfun(x)
            if x in seen:
                continue
            seen.add(x)
            yield x
            
            
def f11(seq): # f10 but simpler
    # Order preserving
    return list(_f11(seq))

def _f11(seq):
    seen = set()
    for x in seq:
        if x in seen:
            continue
        seen.add(x)
        yield x
        

def ordrd(items):
    res =list(OrderedDict.fromkeys(items))
    print res
    return res


def ordrd3(theArray):
    for i in range(len(theArray)-1,-1,-1): #get the indexes in reverse
        if theArray.count(theArray[i]) > 1:
            theArray.pop(i)

def ordrd4(list1):
    list2 = list(set(list1))    
    list2.sort(key=list1.index)    
    return list2


def ordrd2(items):
    list2 = []
    [list2.append(a) for a in items if a not in list2]
    return list2
          
          
          
def ordrd6_(iterable):
    seen = set()
    seen_add = seen.add
    for element in itertools.ifilterfalse(seen.__contains__, iterable):
        seen_add(element)
        yield element
          
def ordrd6(iterable):          
    return list(ordrd6_(iterable))

import time

def timing(f, n, a):
    print f.__name__,
    r = range(n)
    t1 = time.clock()
    for i in r:
        f(a); f(a); f(a); f(a); f(a); f(a); f(a); f(a); f(a); f(a)
    t2 = time.clock()
    print round(t2-t1, 3)
    



def getRandomString(length=10, loweronly=1, numbersonly=0,
                    lettersonly=0):
    """ return a very random string """
    _letters = 'abcdefghijklmnopqrstuvwxyz'
    if numbersonly:
        l = list('0123456789')
    elif lettersonly:
        l = list(_letters + _letters.upper())
    else:
        lowercase = _letters+'0123456789'*2
        l = list(lowercase + lowercase.upper())
    shuffle(l)
    s = ''.join(l)
    if len(s) < length:
        s = s + getRandomString(loweronly=1)
    s = s[:length]
    if loweronly:
        return s.lower()
    else:
        return s

testdata = {}
for i in range(35):
    k = getRandomString(5, lettersonly=1)
    v = getRandomString(100 )
    testdata[k] = v
    
testdata = [int(x) for x in list('21354612')]
testdata += list('abcceeaa5efm')
class X:
    def __init__(self, n):
        self.foo = n
    def __repr__(self):
        return "<foo %r>"%self.foo
    def __cmp__(self, e):
        return cmp(self.foo, e.foo)
        
testdata = []
for i in range(10000):
    testdata.append(getRandomString(3, loweronly=True))
#testdata = ['f','g','c','d','b','a','a']



order_preserving = f2, f4, f5, f5b, f8, f10, f11
order_preserving = ordrd6, f8, f5, f5b, f10, f11,f5, ordrd4, ordrd3

not_order_preserving = f1, f3, f6, f7, f9
testfuncs = order_preserving + not_order_preserving



for f in testfuncs:
    if f in order_preserving:
        print "*",
    timing(f, 500, testdata)
