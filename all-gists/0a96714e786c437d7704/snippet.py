def int2list(n):
    out = []
    while n:
        n, r = divmod(n, 10)
        out.insert(0, r)
    return out