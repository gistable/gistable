import math

def is_whole(x):
    return x % 1 == 0

n = int(raw_input())
c_list = set()

c = 5
while len(c_list) < n:
    for b in xrange(1, c):
        a = math.sqrt(c**2 - b**2)
        if is_whole(a):
            c_list.add(c)
    c += 1

for sol in c_list:
    print(sol)