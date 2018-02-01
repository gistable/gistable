from random import randint
import timeit
import sys


def qsort2(list):
    if list == []: 
        return []
    else:
        pivot = list[0]
        lesser, equal, greater = partition(list[1:], [], [pivot], [])
        return qsort2(lesser) + equal + qsort2(greater)

def partition(list, l, e, g):
    if list == []:
        return (l, e, g)
    else:
        head = list[0]
        if head < e[0]:
            return partition(list[1:], l + [head], e, g)
        elif head > e[0]:
            return partition(list[1:], l, e, g + [head])
        else:
            return partition(list[1:], l, e + [head], g)

def qsort(list):
    if list == []: 
        return []
    pivot = list[0]
    l = qsort([x for x in list[1:] if x < pivot])
    u = qsort([x for x in list[1:] if x >= pivot])
    return l + [pivot] + u

def get_array(n):
    l = []
    for i in range(n):
        l.append(randint(0,n))
    return l

def test(n,i):
    x=get_array(n)
    if i is 1:
        qsort(x)
    else:
        qsort2(x)


if __name__=="__main__":
    sys.setrecursionlimit(10000)
    print "list-compr 1000 elems",timeit.Timer("test(1000,1)",setup="""from __main__ import test""").timeit(100)
    print "recursion 1000 elems",timeit.Timer("test(1000,2)",setup="""from __main__ import test""").timeit(100)

    print "list-compr 2000 elems",timeit.Timer("test(2000,1)",setup="""from __main__ import test""").timeit(100)
    print "recursion 2000 elems",timeit.Timer("test(2000,2)",setup="""from __main__ import test""").timeit(100)
    
