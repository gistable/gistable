'''
cos(x) = 1-x^2/2!+x^4/4!-x^6/6!+..-
'''
import math

def fact(n):
    if n==0:
       return 1 
    else: 
      return n*fact(n-1) 

def pow(x,y):
    p = 1
    for i in range(1,y+1):
        p *= x
    return p

def abs(x,y):
    if x > y:
       return x-y
    else:
       return y-x 

def cos(x):
    eps = 0.0001
    n = 2  
    v1 = 1
    v2 = v1 - pow(x,2)*1.0/fact(2)
    while abs(v1,v2) >= eps:
          v1 = v2
          v2 += pow(-1,n)*pow(x,2*n)*1.0/fact(2*n) 
          n = n + 1
    return v2

print math.cos(5)
