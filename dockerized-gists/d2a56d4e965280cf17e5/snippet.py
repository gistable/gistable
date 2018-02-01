def g(D):
  """
  D = # of features
  O(g(D))
  """
  return sum([D-i for i in xrange(0,D)])
  
# g(20) = 210