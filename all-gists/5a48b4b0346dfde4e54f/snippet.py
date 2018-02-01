from math import sqrt

def is_prime(n):
  print 'Checking {}'.format(n)
  if n == 1: return True
  root = sqrt(n)
  if root % 1 == 0: 
    print "{} isn't prime, with square root of {}".format(n, root)
    return False
  try_factor = 2
  check_bounds = n - 1
  while try_factor < check_bounds:
    if n % try_factor == 0:
      print "{} is factor".format(try_factor)
      return False
    try_factor += 1
    check_bounds = n / try_factor - 1
    print "Trying {} with bounds of {}".format(try_factor, check_bounds)
  print "TRUE: {} is prime.".format(n)
  return True

def find_closest_prime(n, range_limit=1000):
  if is_prime(n):
    prime = n
  else:
    prime = None
    n_higher = n_lower = n
    loops = 0
    while prime is None and loops < range_limit:
      if n_lower > 1:
        n_lower -= 1
        if is_prime(n_lower):
          prime = n_lower
          break
      n_higher += 1
      if is_prime(n_higher):
        prime = n_higher
        break
      print "Neither of {} and {} are primes".format(n_lower, n_higher)
      loops += 1
    if loops == range_limit: print "Loop limit!"
    if prime is None:
      prime = 1
  print "FOUND: Closest prime for {} is {}".format(n, prime)

find_closest_prime(1) # 1
find_closest_prime(2) # 2
find_closest_prime(3) # 3
find_closest_prime(6) # 5
find_closest_prime(12) # 11
find_closest_prime(24) # 23
find_closest_prime(36) # 37
find_closest_prime(121) # 127
find_closest_prime(1000) # 997
