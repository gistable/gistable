#Juan Paulo Farías Rodríguez PIMO 2013-1
#Código: 2091691
#Laboratorio 3



#1

def maximo(X,N,i,m):
    r=0
    if i==N:
        r=m
    else:
        r=maximo(X,N,i+1,max(m, X[i]))

    return r


#2

def vecinas(X,N,i):
    vec=True
    if i==N:
        r=vec
    else:
        r = ((X[i]!= X[i-1]) and (vecinas(X, N, i+1)))   
    return r

#3
def paridad(X, N, i, p):
    if i==N:
       r=p
    else:
        if (X[i]%2==0):
            r= paridad(X, N, i+1, p+1)
        else:
            r=paridad(X, N, i+1, p-1)
    return r        
    
    

    
#4 
def ascendente(X,N,i):
        asc=True
        if i==N:
            r=asc
        else:
            r= (X[i]>= X[i-1]) and ascendente(X, N, i+1)   
        return r



X = [ int(x) for x in input("Deme los elementos del arreglo X\nSeparados por espacios\n").split()]

print ("El máximo valor del arreglo es:\n")
print (maximo(X,len(X),0,0))
print ("\n¿El arreglo tiene celdas vecinas todas distintas?\n")
print (vecinas(X,len(X),1))
print ("\n¿El arreglo tiene igual número de pares que impares?\n")
if (paridad(X,len(X),0,0))==0:
    print ("Sí")
else:
    print ("No")
print ("\n¿El arreglo es ascendente?\n")
print (ascendente(X,len(X),1))