"""
Test:
  Given two strings, `a` and `b`. Sort the letters in `a` by the order of letters in `b`.
  For example:
    a = "ssttexeste"
    b = "test"
    result = "ttteeesssx"
"""

def a_by_b(a, b):
    idx = {c:i for i, c in enumerate(b)}
    m = len(b)
    out = [''] * (m + 1)
    for c in a:
        out[idx.get(c, m)] += c
    return ''.join(out)


a = "adlkfhxaxjxkxhxfwkhkjfhjkahjksedeheflhadslfkhdfjkadhjhdhskghdjdjkhskkhjokhkshakhlhfkjdshjfkshhkskskss"
b = "alskdjfhg"


def bench():
    for i in xrange(100000):
        assert a_by_b(a, b) == "aaaaaallllssssssssssskkkkkkkkkkkkkkkkkkkkdddddddddjjjjjjjjjjjffffffffhhhhhhhhhhhhhhhhhhhhhgxxxxxweeeo"

bench()

# Probably more scalable:

def a_by_b_(a, b):
    idx = {c:i for i, c in enumerate(b)}
    m = len(b)
    buckets = [[] for _ in range(m+1)]
    for c in a:
        buckets[idx.get(c, m)].append(c)
    for l in buckets[1:]:
        buckets[0].extend(l)
    return ''.join(buckets[0])