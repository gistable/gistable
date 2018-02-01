import itertools
import re
import z3

base = 'plaidctf'
r = open('regex_57f2cf49f6a354b4e8896c57a4e3c973.txt').read().strip()

s = re.search(r'\((.*)\)', r).group(1)
s = s.split('|')[3:]
s = [re.findall(r'(.*?)\[(.*?)\]', it) for it in s]

solver = z3.Solver()
sol = z3.Array('sol', z3.IntSort(), z3.BoolSort())

for x in s:
    pos = 0
    rule = []
    for a, b in x:
        m = re.match(r'\.{(\d+)}', a)
        if m:
            pos += int(m.group(1))
        else:
            pos += len(a)
        b = [base.index(it) for it in b]
        b = [bin(it)[2:].rjust(3, '0') for it in b]
        b = zip(*b)
        for j, y in enumerate(b):
            y = [it == '1' for it in y]
            var = sol[pos * 3 + j]
            if all(it == True for it in y):
                rule.append(var)
            elif all(it == False for it in y):
                rule.append(z3.Not(var))
        pos += 1
    solver.add(z3.Or(*rule))

print solver.sexpr()
print solver.check()
sol = solver.model()[sol].as_list()[:-1]
sol = [a.as_long() for a, b in sol if z3.is_true(b)]
val = [0] * 171
for i in sol:
    val[i / 3] |= 1 << (i % 3)
for per in itertools.permutations(base):
    s = ''.join(per[it] for it in val)
    if re.match(r, s) is None:
        print s