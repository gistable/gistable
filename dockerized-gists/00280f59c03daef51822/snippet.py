def sqrt00(n,p,m,v):
        if(n<0):
            return("i"+str(sqrt00(n*-1,p,m*-1,v)))
        if(n == 1 or n == 0):
            return(n)
        if(type(n)==float):
            return(None) # integer only : (
        c = 0
        while(n>=v):
            if(v == n):
                return(p)
            else:
                C = 2 ** c
                inc = C*p*2+C**2
                v += inc
                p += C
                c += 1
        if(C==1):
            return(p-1)
        else:
            m = C
            v -= inc
            p -= C
        return(sqrt00(n,p,m,v))

def sqrt0(n):
    return(sqrt00(n,1,n,1))