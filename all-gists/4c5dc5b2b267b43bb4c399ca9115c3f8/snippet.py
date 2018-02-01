from functools import lru_cache
@lru_cache
def fibonacci(n):
  
  if n == 1:
    return 1
  elif n==2:
    return 1
  elif n> 2:
    return fibonacci(n-2)  + fibonacci(n-1)

for i in range(1, 1000):
  print(i, " : ", fibonacci(i))