def qsort(A, L, U):
  if L < U:
    P = A[L]
    W = L
    for i in range(L, U):
      if A[i] < P:
        W += 1
        tmp = A[i]
        A[i] = A[W]
        A[W] = tmp
    A[L] = A[W]
    A[W] = P
    
    qsort(A, L, W)
    qsort(A, W+1, U)