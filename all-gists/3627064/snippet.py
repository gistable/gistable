def cartesian (lists):
    if lists == []: return [()]
    return [x + (y,) for x in cartesian(lists[:-1]) for y in lists[-1]]

print cartesian([[1, 2, 3], [2, 4, 6], [3, 6, 9]])
