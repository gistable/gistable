class Node:
  def __init__(self,val,nxt):
    self.val = val
    self.nxt = nxt

def prnt(n):
  nxt = n.nxt
  print n.val
  if(nxt is not None):
    prnt(nxt)

#Iterative
def reverse(n):
  last = None
  current = n

  while(current is not None):
    nxt = current.nxt
    current.nxt = last 
    last = current
    current = nxt

  return last

#Recursive
def recurse(n,last):
  if n is None:
    return last
  nxt = n.nxt
  n.nxt = last
  return reverse(nxt, n)


n0 = Node(4,None)
n1 = Node(3,n0)
n2 = Node(2,n1)
n3 = Node(1,n2)

#l = reverse(n3)
prnt(n3)
result = recurse(n3, None)
prnt(result)
