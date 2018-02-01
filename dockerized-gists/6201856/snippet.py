import collections
import sys

# setup the graph
G = {
  1:set([ 2, 3, 5, 6,]),
  2:set([ 1, 4,]),
  3:set([ 1, 6, 7,]),
  4:set([ 2, 5, 7, 8,]),
  5:set([ 1, 4, 6, 8, 9, 10,]),
  6:set([ 1, 3, 5, 7,]),
  7:set([ 3, 4, 6, 9,]),
  8:set([ 4, 5, 9,]),
  9:set([ 5, 7, 8, 20,]),
  10:set([ 5, 11, 12, 14, 15,]),
  11:set([ 10, 12, 13, 14,]),
  12:set([ 10, 11, 13, 14, 15,]),
  13:set([ 11, 12, 15,]),
  14:set([ 10, 11, 12, 25,]),
  15:set([ 10, 12, 13,]),
  16:set([ 17, 19, 20, 21, 22,]),
  17:set([ 16, 18, 19, 20,]),
  18:set([ 17, 20, 21, 22,]),
  19:set([ 16, 17,]),
  20:set([ 9, 16, 17, 18,]),
  21:set([ 16, 18,]),
  22:set([ 16, 18, 23,]),
  23:set([ 22, 24, 25, 26, 27,]),
  24:set([ 23, 25, 26, 27,]),
  25:set([ 14, 23, 24, 26, 27,]),
  26:set([ 23, 24, 25,]),
  27:set([ 23, 24, 25,]),
}
Gvol = 102

# G is graph as dictionary-of-sets
alpha=0.99
tol=0.01
seed=[1]

x = {} # Store x, r as dictionaries
r = {} # initialize residual
Q = collections.deque() # initialize queue
for s in seed: 
  r[s] = 1/len(seed)
  Q.append(s)
while len(Q) > 0:
  v = Q.popleft() # v has r[v] > tol*deg(v)
  if v not in x: x[v] = 0.
  x[v] += (1-alpha)*r[v]
  mass = alpha*r[v]/(2*len(G[v])) 
  for u in G[v]: # for neighbors of u
    assert u is not v, "contact dgleich@purdue.edu for self-links"
    if u not in r: r[u] = 0.
    if r[u] < len(G[u])*tol and \
       r[u] + mass >= len(G[u])*tol:
       Q.append(u) # add u to queue if large
    r[u] = r[u] + mass
  r[v] = mass*len(G[v]) 
  if r[v] >= len(G[v])*tol: Q.append(v)
print str(x)

  
# Find cluster, first normalize by degree
for v in x: x[v] = x[v]/len(G[v])  
# now sort x's keys by value, decreasing
sv = sorted(x.iteritems(), key=lambda x: x[1], reverse=True)
S = set()
volS = 0.
cutS = 0.
bestcond = 1.
bestset = sv[0]
for p in sv:
  s = p[0] # get the vertex
  volS += len(G[s]) # add degree to volume
  for v in G[s]:
    if v in S:
      cutS -= 1
    else:
      cutS += 1
  print "v: %4i  cut: %4f  vol: %4f"%(s, cutS,volS)
  S.add(s)
  if cutS/min(volS,Gvol-volS) < bestcond:
    bestcond = cutS/min(volS,Gvol-volS)
    bestset = set(S) # make a copy
print "Best set conductance: %f"%(bestcond)
print "  set = ", str(bestset)
