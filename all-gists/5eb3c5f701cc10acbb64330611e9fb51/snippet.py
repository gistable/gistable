#!/usr/bin/env python3

import numpy as np

def sorted_merge(l1, l2, verbose = False):
    """
    Merges two lists that are themselves sorted into ascending order
    (almost certainly not optimal!).
    
    l1, l2 : pre-sorted lists to be merged
    
    verbose: print out? 
    """
    len_l1 = len(l1)
    len_l2 = len(l2)

    combined_l = []
    i=0
    while i < len(l1):
        if verbose: print(i, l1[i], l2[0])
        if l1[i] < l2[0]:
            if verbose: print(l1[i], "<", l2[0])
            combined_l.append(l1[i])
        else:
            if verbose: print(l1[i], ">", l2[0])
            combined_l.append(l2[0])
            i=i-1
            l2 = l2[1:]
        i+=1

    if len(l2) > 0:
        combined_l.extend(l2)

    return(combined_l)

if __name__ == "__main__":
    l1 = np.arange(6, 20, 2)
    l2 = np.arange(1, 21, 2)

    print(l1)
    print(l2)
    
    print(sorted_merge(l1, l2))
else:
    pass