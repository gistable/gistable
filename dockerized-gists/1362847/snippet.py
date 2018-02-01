#Gets the index of maximum element in a list. If a conflict occurs, the index of the last largest is returned
def maxl(l): return l.index(reduce(lambda x,y: max(x,y), l))

#Gets the index of minimum element in a list. If a conflict occurs, the index of the last smallest is returned
def minl(l): return l.index(reduce(lambda x,y: min(x,y), l))

#same as above but without the reduce coolness
def maxl(l): return l.index(max(l))

def minl(l): return l.index(min(l))