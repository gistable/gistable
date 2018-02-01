def quicksort(v):
    if len(v) <= 1: 
        return v
    
    pivot = v[0]
    equals  = [x for x in v if x == pivot]
    smaller = [x for x in v if x <  pivot]
    higher = [x for x in v if x >  pivot]
    return quicksort(smaller) + equals + quicksort(higher)

print (quicksort([5, 7, 9, 3, 4, 0, 2, 1, 6, 8]))

