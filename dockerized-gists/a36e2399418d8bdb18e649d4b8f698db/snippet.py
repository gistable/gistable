import numpy as np
import numpy.random as nr
def gen(N):
    X = nr.choice([0,1],size=N,p=[0.6,0.4])
    D = nr.choice([0,1],size=N,p=[0.6,0.4])
    epsi = nr.uniform(0,2,N)
    Y = X+D*epsi
    return X,D,epsi,Y
    
def estim(D,Y):
    Y0 = np.average(Y[D==0])
    Y1 = np.average(Y[D==1])
    return Y1-Y0
    
X,D,epsi,Y = gen(10000)
estim(D,Y)