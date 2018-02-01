# makes Fibonacci numbers using python
def fib(s):
  a = 0
  b = 1
  for i in range(s+1):
  print a
    old_a = a
    a = b
    b = old_a + b

fib(200)
