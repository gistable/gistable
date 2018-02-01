def hack1(n, k):
  def f(s):
    return s.count('1')
  binaries = []
  for x in range(2**n):
    binaries.append(bin(x))
  binaries.sort(key=f, reverse = True)
  return binaries[k - 1]

def hack(n, k):
  return sorted([bin(x) for x in range(2**n)],
                key=lambda s: s.count('1'),
                reverse = True)[k-1]
  
