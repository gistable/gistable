#!/usr/bin/env python3

p = 61
q = 53

n = p*q
phi = (p-1)*(q-1)

# Took from SO
def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    g, y, x = egcd(b%a,a)
    return (g, x - (b//a) * y, y)

def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('No modular inverse')
    return x%m

e = 17
d = modinv(e, phi)

print('P =', p)
print('Q =', q)
print('N =', n)
print('Phi =', phi)
print('E =', e)
print('D =', d)
print('(E*D)%Phi =', (e*d)%phi)
