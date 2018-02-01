import string

ALPHABET = 'ABCDEGHKLPQRSTUVWXYZ' + '23456789'
ALPHABET_REVERSE = dict((c, i) for (i, c) in enumerate(ALPHABET))
BASE = len(ALPHABET)
START_FROM = 1


def encode(n):
    n = n * START_FROM
    s = []
    while True:
        n, r = divmod(n, BASE)
        s.append(ALPHABET[r])
        if n == 0:
            break
    return ''.join(reversed(s))


def decode(s):
    n = 0
    s = s.upper()
    for c in s:
        n = n * BASE + ALPHABET_REVERSE[c]
    return n / START_FROM
