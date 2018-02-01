def compose(f, g):
  return lambda(x):f(g(x))


def composecurry(f):
  return lambda(x) : compose(f,x)

def composevar(*fns):
  acc = (lambda (x) : x)
  for f in fns:
    acc = compose(acc,f)
  return acc


print (compose(lambda(x):(x + 3), (lambda(x):(x*2)))(4))

print (composecurry(lambda (x) : (x+3))(lambda(x):(x*2))(4))


def inc(x):
   return x+1

def mult3(x):
   return x*3

print composevar(inc, inc, inc, inc, mult3)(7)
