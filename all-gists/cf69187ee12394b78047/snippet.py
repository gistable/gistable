#!/usr/bin/env python


'Criba de Atkin: http://es.wikipedia.org/wiki/Criba_de_Atkin'


from __future__ import print_function
from math import sqrt


__author__ = 'Ismael Venegas Castelló'


def criba_atkin(limite):
    primos = [2, 3]
    criba = [False] * (limite + 1)
    factor = int(sqrt(limite)) + 1

    for x in range(1, factor):
        for y in range(1, factor):
            n = 4*x**2 + y**2
            if n <= limite and (n % 12 == 1 or n % 12 == 5):
                criba[n] = not criba[n]

            n = 3*x**2+y**2
            if n <= limite and n % 12 == 7:
                criba[n] = not criba[n]

            n = 3*x**2 - y**2
            if x > y and n <= limite and n % 12 == 11:
                criba[n] = not criba[n]

    for x in range(5, factor):
        if criba[x]:
            for y in range(x**2, limite + 1, x**2):
                criba[y] = False

    for i in range(5, limite + 1):
        if criba[i]:
            primos.append(i)

    return primos