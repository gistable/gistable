def Y(func):
  def _(f):
    return f(f)
  def o(O):
    def x(X):
      return O(O)(X)
    return func(x)
  return _(o) # o_O

def fizzbuzz(c):
  def fb(n, o):
    def _fb(i):
      return "" if i % n else o
    return _fb
  def f(n):
    if not n:
      return []
    else:
      return c(n - 1) + [(fb(3, "fizz")(n) + fb(5, "buzz")(n)) or n]
  return f
 
f = Y(fizzbuzz)
print f(100)