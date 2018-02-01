import pickle
from math import log, ceil, floor

def encodetoint(str):
    str = pickle.dumps(str)
    base = 256
    val = 0
    for i in xrange(len(str)):
        val += base ** i * ord(str[i])
    return val

def decodefromint(enc):
    base = 256
    li = []
    countrange = int(\
         ceil(\
         log(enc, base)))
    count = range(countrange)
    count.reverse()
    for i in count:
        li = [(int(floor(enc / (base ** i + 0.0))))] + li
        enc -= li[0] * base ** i
    return pickle.loads(''.join([chr(i) for i in li]))


def xorswap(a, b):
    # Takes two ints and swaps them
    a = a ^ b
    b = a ^ b
    a = a ^ b
    return (a, b)

def main():
    a = "FooBar"
    b = 1924
    print "Value of a:", a, "\nValue of b:", b
    a = encodetoint(a)
    b = encodetoint(b)
    a, b = xorswap(a, b)
    a = decodefromint(a)
    b = decodefromint(b)
    print "Value of a:", a, "\nValue of b:", b


if __name__ == "__main__":
    main()
