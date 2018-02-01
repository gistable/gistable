def WMF(R,k=2,alpha=0.1):
    m,n=R.shape
    X=rand(m,k)
    Y=rand(n,k)
    for itr in xrange(10000):
        Xold=X.copy()
        Yold=Y.copy()
        for i in xrange(m):
            ri=R[i]
            C=(ri!=0)*1
            if sum(C)==0:
                continue
            X[i]=dot(pinv(dot(Y.T,c_[C]*Y)+alpha*identity(k)),dot(Y.T,C*ri))
        for j in xrange(n):
            rj=R[:,j]
            C=(rj!=0)*1
            if sum(C)==0:
                continue
            Y[j]=dot(pinv(dot(X.T,c_[C]*X)+alpha*identity(k)),dot(X.T,C*rj))
        if norm(X-Xold)+norm(Y-Yold)<1e-6:
            break
    return X,Y
# R=X.dot(Y.T)