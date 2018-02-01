def sieve(numbers, n):
    for i in range(n * 2, len(numbers), n):
        numbers[i] = False

def skip_to_next_prime(numbers, n):
    n += 1
    while n < max and not numbers[n]:
        n += 1
    return n

def primes(max):
    '''generate primes less than max'''
    max = int(max ** .5)
    numbers = [False, False] + [True] * max
    n = 2
    while n < max:
        sieve(numbers, n)
        n = skip_to_next_prime(numbers, n)

    return [i for i in range(max) if numbers[i]]

#n = 13195
n = 600851475143
print [x for x in primes(n) if n % x == 0]