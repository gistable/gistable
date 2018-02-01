# Example usage
# $ python dft.py | gnuplot
# 9
# 0 0
# 1 1
# 2 2
# 0 2
# 1 1
# -1 1
# 0 2
# -2 2
# -1 1

import math

N = int(raw_input())

f = []
for i in range(N):
    (x, y) = map(float, raw_input().split())
    f.append(complex(x, y))

F = []
for i in range(N):
    ang = -2 * 1j * math.pi * i / N
    r = 0
    for j in range(N):
        r += (math.e ** (ang * j)) * f[j]
    F.append(r)

print "set parametric"
print "set samples", N + 1

print "x(t)=",
for i in range(N):
    ang = 2 * math.pi * i / N
    if i > 0:
        print "+",
    print F[i].real / N, "*cos(", ang, "*t)-",
    print F[i].imag / N, "*sin(", ang, "*t)",

print
print "y(t)=",
for i in range(N):
    ang = 2 * math.pi * i / N
    if i > 0:
        print "+",
    print F[i].imag / N, "*cos(", ang, "*t)+",
    print F[i].real / N, "*sin(", ang, "*t)",

print
print "plot [t=0:", N, "] x(t), y(t)"
print "pause 60"