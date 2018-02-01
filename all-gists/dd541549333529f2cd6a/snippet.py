def sfn1(na, o):
    a, b, c = na[o-2], na[o-1], na[o]
    if a == b and b == c:
        return 1
    df = b - a
    if df == c - b:
        return 2 if abs(df) == 1 else 5
    elif a == c:
        return 4
    return 10


def sfn2(na, o):
    a, b, c, d = na[o-3], na[o-2], na[o-1], na[o]
    if a == b and b == c and c == d:
        return 1
    df = b - a
    if df == c - b and df == d - c:
        return 2 if abs(df) == 1 else 5
    elif a == c and b == d:
        return 4
    return 10


def sfn3(na, o):
    a, b, c, d, e = na[o-4], na[o-3], na[o-2], na[o-1], na[o]
    if a == b and b == c and c == d and d == e:
        return 1
    df = b - a
    if df == c - b and df == d - c and df == e - d:
        return 2 if abs(df) == 1 else 5
    elif a == c and b == d and c == e:
        return 4
    return 10


def score(na):
    ln = len(na)
    msa = [0] * (ln+2)
    i = 0
    mn = 10 * 100000
    while i < ln:
        ms = mn
        if i < 2:
            msa[i] = 10
        else:
            for fi, sf in enumerate([sfn1, sfn2, sfn3]):
                s = sf(na, i)
                if msa[i-fi-3] + s < ms:
                    ms = msa[i-fi-3] + s
            msa[i] = ms
        i += 1
    return msa[-3]


if __name__ == "__main__":
    for c in xrange(int(raw_input())):
        t = [int(v) for v in list(raw_input())]
        print score([int(i) for i in list(t)])
