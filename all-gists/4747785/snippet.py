####################################
# Copyright Christopher Abiad, 2012
# All Rights Reserved
####################################

__author__ = 'Christopher Abiad'

def mergesort(l):
    n = len(l)
    if n <= 1:
        return l
    return merge(mergesort(l[:n/2]), mergesort(l[n/2:]))

def merge(l1, l2):
    result = []
    i1 = 0
    i2 = 0
    while i1 < len(l1) and i2 < len(l2):
        if l1[i1] <= l2[i2]:
            result.append(l1[i1])
            i1 += 1
        else:
            result.append(l2[i2])
            i2 += 1
    if i1 < len(l1):
        result.extend(l1[i1:])
    else:
        result.extend(l2[i2:])
    return result

# Test code follows
from pprint import pprint
if __name__ == '__main__':
    pprint(mergesort([3,4,1,9]))
    pprint(mergesort([86,7,5,30,9]))
    pprint(mergesort([1,2,3,4,5]))
    pprint(mergesort([5,4,3,2]))
    pprint(mergesort([1]))
    pprint(mergesort([]))