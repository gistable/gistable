#!/bin/python
'''
@author ademar
encontrar os 2 primos que somados formam um numero par
'''

import sys

def getPrimeUpTo(x):
        print "getting prime numbers up to", x
        primes = [2]
        for i in range(3,x,2):
                add = True
                for p in primes:
                        if (i % p == 0):
                                add = False
                                break
                if (add):
                        primes.append(i)
        print len(primes), "primes number up to", x
        return primes

def getTwoPrimesOf(x):
        primes = getPrimeUpTo(x)
        primesOfX = []
        print "getting two primes..."
        for p in primes:
                if (x-p in primes):
                        if(not [x-p, p] in primesOfX):
                                primesOfX.append([p, x-p])
        return primesOfX

def main():
        if (len(sys.argv)<=1):
                print "send-me a number your dumb!"
        else:
                try:
                        x = int(sys.argv[1])
                except:
                        print sys.argv[1], "isn't a number your dumb!"
                        return

                if (x % 2 != 0):
                        print x, "is a odd number, please send-me a pair number"
                elif (x <= 2):
                        print x, "is less or equals then 2, please send-me a number bigger"
                else:
                        primesOfX = getTwoPrimesOf(x)
                        print "Founded", len(primesOfX), "set of primes:"
                        print primesOfX
main()