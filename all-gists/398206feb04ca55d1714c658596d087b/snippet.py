def separar(quantity):
    moneys = [50, 20, 10, 5, 2, 1, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01]
    quantities = {m: 0 for m in moneys} 
    for m in moneys:      
        while quantity >= m:
            quantity -= m
            quantities[m] += 1           
    return quantities

#versao alternativa

def notas_moedas(n):
    cash=(50,20,10,5,2,1,0.50,0.20,0.10,0.05,0.02,0.01)
    euros=int(n)
    centimos=n-euros
    res={}
    for e in cash:
        if e>=1:
            if euros//e>0:
                res[e]=euros//e
                euros= euros-(e*(euros//e))
        elif e<1:
            if centimos//e>0:
                res[e]=centimos//e
                centimos= centimos-(e*(centimos//e))
    return res