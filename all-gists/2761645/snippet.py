#!/usr/bin/env python
#-*-coding:UTF-8-*-

def f((q, r, t, k)):
    n = (3 * q + r) / t
    if (4 * q + r) / t == n:
        return (10 * q, 10 * (r - n * t), t, k, n)
    else:
        return (q * k, q * (4 * k + 2) + r * (2 * k + 1), t * (2 * k + 1), k + 1)

def pi(n = -1):
    out = ''
    printed = False
    r = f((1, 0, 1, 1))
    out = ''
    while (n != 0):
        if len(r) == 5:
            out += str(r[4])
            if not printed:
                out += '.'
                printed = True
            n -= 1
        r = f(r[:4])
    return out

def main():
    print pi(100)

if __name__ == "__main__":
    main()