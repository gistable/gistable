# Based on http://www.ams.org/notices/201208/rtx120801094p.pdf

import math

EPS = 1e-8

# Arithmetico-geometric mean
def agm(a, b):
    while True:
        a1 = 0.5*(a+b)
        b1 = math.sqrt(a*b)
        if abs(a-a1) < EPS:
            return a1
        a = a1
        b = b1

# Modified arithmetico-geometric mean
def magm(a, b):
    c = 0
    while True:
        a1 = 0.5*(a+b)
        u = math.sqrt((a-c)*(b-c))
        b1 = c+u
        c1 = c-u
        if abs(a-a1) < EPS:
            return a1
        a = a1
        b = b1
        c = c1

# Compute elliptic integral of second kind
def E(e):
    return math.pi*magm(1, 1-e)/(2*agm(1, math.sqrt(1-e)))

# Assumes a > b and that b != 0
def perimeter(a, b):
    return 4*a*E(1-b**2/a**2)

# Example
print perimeter(0.75, 0.321)
