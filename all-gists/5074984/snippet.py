def quicksortTest(A,p,r):
  print A
  if (p<r):
    q = partition(A,p,r)
    print "********************************************** q=, ", q, "   r=", r
    quicksortTest(A,q+1,r)
  if (p==r):
    print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! p = r", p, r
    q = partition(A,p,r)
    quicksortTest(A,0,q-1)
    #quicksortTest(A,p,q)



def partition(A, p, r):
  x = A[p]
  print "Pivot: ", x
  i = p-1
  j = r+1
  while True:
    while True:
      j -= 1
      print "working from the end, comparing", A[j], " and ", x
      if (A[j]<=x):
        print A[j], " <= ", x
        break
    while True:
      i += 1
      print "working from the beginning, comparing", A[i], " and ", x
      if (A[i]>=x):
        print A[i], " >= ", x
        break
    if (i<j):
      print "Switching, ", A[i], " with ", A[j]
      A[i], A[j] = A[j], A[i]
      print A
    else:
      print i, " is not less than ", j
      return j


def hoare(a, p, r):
  x = a[p]
  i, j = p-1, r+1
  while True:
    while True:
      j -= 1
      if a[j] <= x:
        break
    while True:
      i += 1
      if a[i] >= x:
        break
    if i < j:
      print "Switching, ", a[i], " with ", a[j]
      a[i], a[j] = a[j], a[i]
    else:
      return j

Array = [2,8,7,1,3,5,6,4]
p = 0
r = len(Array) - 1
print "*** START ***"
quicksortTest(Array,p,r)
print "***  END  ***"
