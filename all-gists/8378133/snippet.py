import functools

def scanl(f,x,it):
  return functools.reduce(lambda xs, y:  xs + [f(xs[-1],y)], it, [x])

def scanl1(f, it):
  return scanl(f, it[0], it[1:])

def scanr1(f, it):
  return reversed(scanl1(f, list(reversed(it))))

def waterflow(levels):
  h_left  = scanl1(max, levels)
  h_right = scanr1(max, levels)
  waterheighs = [min(left,right) for left,right in zip(h_left, h_right)]
  return sum([h - l for h,l in zip(waterheighs, levels)])

print(waterflow([5, 5, 1, 2, 3, 4, 7, 7, 6, 0, 1]))
