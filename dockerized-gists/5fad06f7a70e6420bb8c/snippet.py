def fuzzyfinder(p, l):
        return map(lambda t: t[0], sorted(filter(lambda t: all(map(lambda x: x != -1, t[1])), map(lambda s: (s,map(s.find, p)), l)), key=lambda t: t[1]))
