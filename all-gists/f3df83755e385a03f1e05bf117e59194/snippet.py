def primes(n):
    i = 1
    potential_prime_number = 1
    while True:
        if (i > n):
            return
        potential_prime_number += 1
        while not is_prime(potential_prime_number):
            potential_prime_number += 1
        yield potential_prime_number
        i += 1

def is_prime(potential_prime_number):
    if potential_prime_number < 2: return False
    for x in range(2, int(potential_prime_number ** .5) + 1):
        if potential_prime_number % x == 0:
            return False
    return True

f = primes(10000)
i = 0
for item in f:
    i += 1
    print(i, item)