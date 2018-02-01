fibs = [1,2]
index = 0
while True:
  nextIndex = index + 1
  fib = fibs[index]
  nextFib = fibs[nextIndex]
  newFib = fib + nextFib
  if newFib > 4000000:
    break
  fibs = fibs + [newFib]
  index = index + 1

total = 0
for fib in fibs:
  if fib % 2 == 0:
    total = total + fib

print total