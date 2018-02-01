#!/usr/bin/python
def f(x):
    return x*x

def fastmodexp(x, y, mod):
    p = 1
    aux = x
    while y > 0:
        if y % 2 == 1:
            p = (p * aux) % mod
        aux = (aux * aux) % mod
        y = y >> 1
    return p

def main():
    x = int(raw_input("Escribe tu x -> "))
    d = int(raw_input("Escribe tu d -> "))
    n = int(raw_input("Escribe tu n -> "))
    y = f(x)
    r = fastmodexp(y, d, n)
    print "Esta es tu r = " + str(r)

main()