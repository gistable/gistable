# Print each permutation.
def perm(l, n, str_a):
    if len(str_a) == n:
        print str_a
    else:
        for c in l:
            perm(l, n, str_a+c)

# Return a list of permutations.
def perm2(l, n, str_a, perm_a):
    if len(str_a) == n:
        return [str_a] + perm_a
    else:
        new_perm_a = perm_a
        for c in l:
            new_perm_a = perm2(l, n, str_a+c, new_perm_a)
        return new_perm_a

perm(['a','b','c'], 3, "")

print perm2(['a','b','c'], 3, "", [])