def solution(A):
    import math
    
    N = len(A)
    fib_maxarg = int(math.sqrt(N)) + 10
    
    def fib(n):
        """ Compute nth Fibonacci number """
        if not hasattr(fib, 'mem'):
            fib.mem = [0]*fib_maxarg
            fib.mem[1] = 1
            
        def fibrec(n):
            if n <= 1 or fib.mem[n] > 0:
                return fib.mem[n]
                
            fib.mem[n] = fibrec(n-1) + fibrec(n-2)
            return fib.mem[n]
        
        return fibrec(n)
    
    # get all F(N) that are <= N-1
    fibs, i = [], 0
    while len(fibs)==0 or fibs[-1] < N+1:
        fibs.append( fib(i) )
        i += 1
    
    # use dynamic programming to compute 
    # B[k] : min number of fib-steps to get from -1 to k
    B = [-1] * (N+1)
    
    for i in xrange(0,N+1):
        leaf = lambda k: k>=N or A[k]==1
        
        if not leaf(i):
            B[i] = 0
        else:
            # OPT: could use bisect, but its still O(logn)
            if i+1 in fibs:
                B[i] = 1
            else:
                # don't check F(0) as we need to make a step
                # also only take into account previous B[k]
                # which present a viable way
                candidates = []
                for f in fibs[1:]:
                    if i-f >= 0 and B[i-f] > 0:
                        candidates.append(B[i-f] + 1)
                
                B[i] = min(candidates) if len(candidates)>0 else 0
    
    return B[N] if B[N] > 0 else -1
    