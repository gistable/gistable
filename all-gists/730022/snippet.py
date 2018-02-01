from sys import argv
from fractions import gcd
primes = [2, 3]
def isprime(p):
  if p == 2: return True
  if p % 2==0: return False
  max = p**0.5+1
  i=3
  while i <= max:
    if p%i==0: return False
    i+=2
  return True
for i in range(0, int(argv[1])):
  q=sorted(primes)[i]
  for i in range(0, q-2):
    i+=1
    p=int((i**2)+i+q)
    if isprime(p)==True:
      if p not in primes:
        primes.append(p)
print len(primes)
print sorted(primes)[:200]