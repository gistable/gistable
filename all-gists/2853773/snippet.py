def firstUniqueChar(st):
    return [x for x in list(st) if list(st).count(x) == 1][0]

print firstUniqueChar("chickheni")