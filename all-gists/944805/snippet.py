def qsort(l):
    """
    >>> qsort([])
    []
    >>> qsort([-1])
    [-1]
    >>> qsort([1, 2, 3, 4])
    [1, 2, 3, 4]
    >>> qsort([4, 3, 2, 1])
    [1, 2, 3, 4]
    >>> qsort([5, 2, 7, 1, 3, 10, 8])
    [1, 2, 3, 5, 7, 8, 10]
    """
    if len(l) < 2:
        return l
    h, t = l[0], l[1:]
    return qsort([u for u in t if u < h]) + [h] + qsort([u for u in t if u >= h])


if __name__ == '__main__':
    import doctest
    doctest.testmod()
