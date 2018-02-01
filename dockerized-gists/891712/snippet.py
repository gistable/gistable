def deBruijn(n, k):
   '''
   An implementation of the FKM algorithm for generating the de Bruijn
   sequence containing all k-ary strings of length n, as described in
   "Combinatorial Generation" by Frank Ruskey.
   '''
 
   a = [ 0 ] * (n + 1)
   
   def gen(t, p):
      if t > n:
         for v in a[1:p + 1]:
           yield v
      else:
         a[t] = a[t - p]
         
         for v in gen(t + 1, p):
           yield v
         
         for j in xrange(a[t - p] + 1, k):
            a[t] = j
            for v in gen(t + 1, t):
              yield v
   
   return gen(1, 1)
 
 
if __name__ == '__main__':
   print ''.join([ chr(ord('A') + x) for x in deBruijn(3, 26) ])