from math import log

def shannon(seq, base=2):

    length = len(seq)
    n = set(seq)
    p = lambda x: seq.count(x) / length

    return -sum(p(i) * log(p(i), base) for i in n)