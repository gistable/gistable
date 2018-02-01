from bisect import bisect_left
from sys import stdin

def is_palin(n):
    s = str(n)
    return s == s[::-1]

def fair(n):
    return is_palin(n) and is_palin(n**2)

def generate(length_limit):
    results = set(('0','1','2','3','11','22'))

    def gen(prefix):
        if len(prefix) > length_limit: return
        for x in '012':
            odd = prefix + x + prefix[::-1]
            even = prefix + x + x + prefix[::-1]
            if fair(int(odd)): 
                results.add(odd)
            if fair(int(even)): 
                results.add(even)
                gen(prefix+x)
    gen('1')
    gen('2')
    return map(int, results)

def from_to(lst, left, right):
    """Finds the number of integeres in the lst that 
        fall into range [left,right]"""
    a = bisect_left(lst, left)
    b = bisect_left(lst, right+1)
    return b - a

#roots = filter(fair, range(10**8))
roots = sorted(list(generate(30)))
palins = [x**2 for x in roots]

cases = int(stdin.readline())
for case in range(1, cases+1):
    a, b = (int(x) for x in stdin.readline().split())
    print "Case #{}: {}".format(case, from_to(palins, a, b))