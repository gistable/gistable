# Implementation based on attack from
# http://www.hpl.hp.com/techreports/1999/HPL-1999-90.pdf
import socket
import telnetlib
import random
from hashlib import sha1
from sage.all import inverse_mod, matrix, vector

TARGET = ('185.143.173.36', 1337)
sock=socket.create_connection(TARGET)

def ru(st):
    buf=''
    while not st in buf:
        c = sock.recv(1)
        buf += c
    return buf

q = 0x100000000000000000001f4c8f927aed3ca752257
bits = 5
n = 50

def oracle(msg):
    ru('-> ')
    sock.sendall('S\n')
    ru('sign: ')
    sock.sendall(msg + '\n')
    r, s, klo = map(int,ru('\n').strip().split(', '))
    return r, s, klo

def dot(a, b):
    return sum(x*y for x, y in zip(a,b))

def babai(A, w):
    ''' http://sage-support.narkive.com/HLuYldXC/closest-vector-from-a-lattice '''
    C = max(max(row) for row in A.rows())
    B = matrix([list(row) + [0] for row in A.rows()] + [list(w) + [C]])
    B = B.LLL(delta=0.99)
    return w - vector(B.rows()[-1][:-1])

msg = 'foo'
h = int(sha1(msg).hexdigest(), 16)
M = 2**bits

sigs = []

print 'Filling buffer...'
iter = 0
while True:
    iter += 1
    n = 50
    sigs.append(oracle(msg))
    while len(sigs) < n+1:
        sigs.append(oracle(msg))

    print 'Iteration %d' % iter

    (r0, s0, klo0) = sigs[-n-1]
    r0inv = inverse_mod(r0, q)

    svec, tvec = [], []
    for idx in range(-n,0):
        (r, s, klo) = sigs[idx]
        t = inverse_mod(-s, q)
        A = (h*(1-r*r0inv)*t)%q
        B = (r*r0inv*s0*t)%q

        inv = inverse_mod(M, q)
        t = ((A + B*klo0 + klo)*inv)%q
        s = (B*M*inv)%q
        svec.append(s)
        tvec.append(t)

    A = [[-1]+svec] + [[0]*i + [q] + [0]*(n-i) for i in range(1, n+1)]

    A = matrix(A)
    t = vector([0]+tvec)
    w = babai(A,t)
    z = w-t

    k = z[0]*M + klo0
    x = (s0*k - h) * inverse_mod(r0, q) % q
    x = hex(int(x)).rstrip('L').lstrip('0x')
    while len(x) %2 :
        x = '0'+x
    x = x.decode('hex')
    if all(ord(c) >= 0x20 and ord(c) <= 0x7d for c in x):
        print x
        exit()
