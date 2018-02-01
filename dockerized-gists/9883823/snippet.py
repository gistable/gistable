def insertion_sort(a):
    ''' implement insertion sort'''
    for i in xrange(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0: 
            if a[j] > key:
                a[j], a[j+1] = a[j + 1], a[j]
            j = j - 1
       

def random_partition(a, lo, hi):
    
    pos = random.randint(lo, hi)
    a[lo], a[pos] = a[pos], a[lo]
    pivot = a[lo]
    left = lo + 1
    right = hi
    
    
    while left <= right:
        while a[left] < pivot:
            left += 1
        while a[right] > pivot:
            right -= 1
        if left <= right:
            a[left], a[right] = a[right], a[left]
            left += 1
            right -= 1
    a[lo], a[right] = a[right], a[lo]
    return right

def smallert_qsort(a, lo, hi):
    if lo < hi:
        if hi - lo <= 32:
            insertion_sort(a)
            return
        else:
            p = random_partition(a, lo, hi)
            if p - lo < hi - p:
                smaller_qsort(a, lo, p - 1)
                lo = p + 1
            else:
                smaller_qsort(a, p + 1, hi)
                hi = p - 1
                
                