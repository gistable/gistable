def quicksort(datos, primero, ultimo):
    i = primero
    j = ultimo
    pivote = (datos[primero] + datos[ultimo]) / 2
 
    while i < j:
        while datos[i] < pivote:
            i+=1
        while datos[j] > pivote:
            j-=1
        if i <= j:
            aux = datos[i]
            datos[i] = datos[j]
            datos[j] = aux
            i+=1
            j-=1
 
    if primero < j:
        datos = quicksort(datos, primero, j)
    if ultimo > i:
        datos = quicksort(datos, i, ultimo)
 
    return datos