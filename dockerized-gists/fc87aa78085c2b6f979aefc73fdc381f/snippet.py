#!/usr/bin/python
import sys

# Credit: https://crypto.stackexchange.com/questions/52292/what-is-fast-prime
generators = [
    (2, 11), (6, 13), (8, 17), (9, 19), (3, 37), (26, 53), (20, 61), (35, 71),
    (24, 73), (13, 79), (6, 97), (51, 103), (53, 107), (54, 109), (42, 127),
    (50, 151), (78, 157),
]

# Precalculate residues to speed up check
# -> calculate all possible n mod p where n ^ r mod p = 1
tests = []
for r, p in generators:
    l = []
    for i in range(p):
        if (i ** r) % p == 1:
            l.append(i)
    tests.append((p, set(l)))

# tests is equivalent to the original test masks,
# minus red herring entries with all bits set

# Equivalent to the original implementation
def is_vulnerable(modulus):
    return all(modulus % p in l for p, l in tests)

# Slower version, but using the generators directly with no precalc
def is_vulnerable_slower(modulus):
    return all(pow(modulus, r, p) == 1 for r, p in generators)

if __name__ == "__main__":
    if is_vulnerable(int(sys.argv[1],0)):
        print("Vuln!")
    else:
        print("OK!")
