s = input()
s += '#'
it = -1

dict = {'H' :  1,
        'C' : 12,
        'N' : 14,
        'O' : 16,
        'Na': 23,
        'P' : 31,
        'S' : 32,
        'Cl': 35.5}

def atom():
    global it
    if s[it:it+2] in dict:
        return dict[s[it:it+2]]
    return dict[s[it]]

def number():
    global it
    n = 0
    while s[it+1] >= '0' and s[it+1] <= '9':
        n = n * 10 + int(s[it+1])
        it += 1
    if n == 0:
        return 1
    return n

def molecule():
    global it
    it += 1
    if s[it] == '#' or s[it] == ')':
        return 0
    if s[it] == '(':
        return molecule() * number() + molecule()
    return atom() * number() + molecule()

print(molecule())
