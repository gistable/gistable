def bits(n):
    b = []
    while n > 0:
        b.append(n % 2)
        n >>= 1
    return reversed(b)

def montgomery_pow(x, n):
    a, b = 1, x
    for x in bits(n):
        if x == 0:
            a, b = a * a, a * b
        else:
            a, b = a * b, b * b
    return a
