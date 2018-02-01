def quicksort(V):
    if len(V) <= 1: 
        return V
    
    pivot = V[0]
    equal = [x for x in V if x == pivot]
    lesser = [x for x in V if x < pivot]
    greater = [x for x in V if x > pivot]
    return quicksort(lesser) + equal + quicksort(greater)