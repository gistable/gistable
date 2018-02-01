from itertools import count

def filter(input, prime):
    for i in input:
        if i % prime:
            yield i

def get_primes(num):
    g = count(2)
    for _ in xrange(num):
        prime = g.next()
        yield prime
        g = filter(g, prime)

for num in get_primes(10):
    print num
