from heapq import heappush, heappop
def heapsort(v):
  h = []
  for x in v:
    heappush(h, x)
  return [heappop(h) for i in range(len(h))]

from random import shuffle
v = list(range(8))
shuffle(v)
print (v)
v = heapsort(v)
print (v)