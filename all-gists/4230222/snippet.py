from math import log
log2= lambda x:log(x,2)
from scipy import histogram, digitize, stats, mean, std
from collections import defaultdict

def mutual_information(x,y):
    return entropy(y) - conditional_entropy(x,y)

def conditional_entropy(x, y):
    """
    x: vector de numeros reales
    y: vector de numeros enteros

    devuelve H(Y|X)
    """
    # discretizacion de X 
    hx, bx= histogram(x, bins=x.size/10, density=True)

    Py= compute_distribution(y)
    Px= compute_distribution(digitize(x,bx))

    res= 0
    for ey in set(y):
        # P(X | Y)
        x1= x[y==ey]
        condPxy= compute_distribution(digitize(x1,bx))

        for k, v in condPxy.iteritems():
            res+= (v*Py[ey]*(log2(Px[k]) - log2(v*Py[ey])))
    return res
        
def entropy(y):
    """
    Computa la entropia de un vector discreto
    """
    # P(Y)
    Py= compute_distribution(y)
    res=0.0
    for k, v in Py.iteritems():
        res+=v*log2(v)
    return -res

def compute_distribution(v):
    """
    v: vector de valores enteros

    devuelve un diccionario con la probabilidad de cada valor
    computado como la frecuencia de ocurrencia
    """
    d= defaultdict(int)
    for e in v: d[e]+=1
    s= float(sum(d.values()))
    return dict((k, v/s) for k, v in d.items())
