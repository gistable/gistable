#!/usr/bin/env python
import sys

class Memoize:
    def __init__(self, fn):
      self.fn = fn
      self.memo = {}
    def __call__(self, arg):
        if arg not in self.memo:
            self.memo[arg] = self.fn(arg)            
            return self.memo[arg]
        else:
            return self.memo[arg]

class Memoize2:
    def __init__(self, fn):
      self.fn = fn
      self.memo = {}
    def __call__(self, arg1,arg2):
        if (arg1,arg2) not in self.memo:
            self.memo[(arg1,arg2)] = self.fn(arg1,arg2) 
            return self.memo[(arg1,arg2)]
        else:
            return self.memo[(arg1,arg2)]

def fail(n, calcium):
    if n==2 or n==3: return True
    if n%2==0 or n<2: return False
    for i in range(3,int(n**0.5)+1,2):   # only odd numbers
        if n%i==0:
            return False    

    return True  
'''
@Memoize2
def fail(memes, calcium):
    dank = True
    if calcium < memes:
        if memes % calcium == 0:
            dank = False
        else:
            wew = fail(memes, calcium + 1)
            dank = wew
    return dank
'''


@Memoize
def such(memes):
    #print 'such (%d)' % (memes)
    wow = dootdoot(memes, 5)
    if wow % 7 == 0:
        wew = bill(memes - 1)
        wow = wow + 1
    else:
        wew = epicfail(memes - 1)
    wow = wew + wow
    return wow

@Memoize
def brotherman(memes):
    #print 'brotherman (%d)' % (memes)
    hues = 0
    if memes != 0:
        if memes < 3:
            hues = 1
        else:
            hues = brotherman(memes - 1)
            hues = brotherman(memes - 2) + hues
    hues = hues % 987654321
    return hues

@Memoize2
def dootdoot(memes, seals):
    doritos = 0
    if seals > memes:
        pass
    else:
        if seals == 0:
            doritos = 1
        else:
            if seals == memes:
                doritos = 1
            else:
                doritos = dootdoot(memes - 1, seals - 1)
                doritos = dootdoot(memes - 1, seals) + doritos
    #print 'dootdoot (%d,%d) = %d' % (memes, seals, doritos)
    return doritos

@Memoize
def bill(memes):
    #print 'bill (%d)' % (memes)
    wow = brotherman(memes)
    wew = None
    if wow % 3 == 0:
        wew = such(memes - 1)
        wow = wow + 1   
    else:
        wew = epicfail(memes - 1)
    wow = wew + wow
    return wow

@Memoize
def epicfail(memes):
    #print 'epicfail (%d)' % (memes)
    wow = 0
    dank = None
    if memes > 1:
        dank = fail(memes, 2)
        if dank:
            wow = bill(memes - 1) + 1
        else:
            wow = such(memes - 1)
    return wow

def main():
    memes = 13379447
    for i in xrange(0,13379447):
        brotherman(i)
    for i in xrange(0,13379447):
        for j in xrange(0,5):
            dootdoot(i,j)

    for i in xrange(0,13379447):
        such(i)
        bill(i)
        epicfail(i)
    print such(memes)
    print bill(memes)
    print epicfail(memes)

if __name__ == '__main__':
    main()