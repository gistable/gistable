def merge(lhs, rhs):
    lhs, rhs = lhs[:], rhs[:]
    merged_list = []
    while bool(lhs) and bool(rhs):
        if lhs[0] <= rhs[0]:
            merged_list.append(lhs.pop(0))
        else:
            merged_list.append(rhs.pop(0))
    return merged_list + lhs + rhs


def merge_sort(L):
    if len(L) == 1:
        return L
    elif len(L) == 2:
        return merge([L[0]], [L[1]])
    else:
        split = len(L)//2
        LHS = merge_sort(L[:split])
        RHS = merge_sort(L[split:])
        return merge(LHS, RHS)
