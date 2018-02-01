#!/usr/bin/env python

import os

def zad1_1(a, b):
    
    sumaa = 0
    sumab = 0
    i     = 1
       
    while i < a and i < b: 
        if  a%i == 0:
            sumaa += i
            print "a: "+str(i)

        if  b%i  == 0:
            sumab += i    
            print "b: "+str(i)
        i += 1
    
    print 'SUMA a '+str(sumaa)+"\n\n"
    print 'SUMA b '+str(sumab)+"\n\n"    
                    
    if sumaa-1 == b and sumab-1 == a:
        print 'yes'
    else:
        print 'no'

def zad1_2(a):
    
    i = 1
    suma  = 0  
    suma2 = 0
    
    while i < a:
        if a%i == 0:
            suma += i
        i += 1    
    
    i = 1        
    while i < (suma-1):
        if (suma-1)%i == 0:
            suma2 += i
        i += 1    

    if suma2-1 == a:
        print "YES \n"
        print "a = "+str(a)
        print "b = "+str(suma-1)
    else:
        print "NO"        
           
    

if __name__ == '__main__':
    #zad1_1(140,195)
    print "\n############\n"
    zad1_2(140)
    
        
