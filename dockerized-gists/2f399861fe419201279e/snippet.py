

# m + n
# element expressed as (pos, value)
def multiply1(vec1, vec2):
    i = 0
    j = 0
    vec = []
    while i < len(vec1) and j < len(vec2):
        if vec1[i][0] > vec2[j][0]:
            j += 1
        elif vec1[i][0] < vec2[j][0]:
            i += 1
        else:
            vec.append((vec1[i][0], vec1[i][1]*vec2[i][1]))
    return vec


def binary_search(vec, i):
    left = 0
    right = len(vec)-1
    while left < right:
        mid = (left+right)>>1
        if vec[mid][0] < i:
            left = mid+1
        elif vec[mid][0] > i:
            right = mid-1
        else:
            return mid
    return left


# m * lgn
# binary search
# when m is much smaller than n
def multiply2(vec1, vec2):
    vec = []
    k = 0
    for element in vec1:
        i, val = element[0], element[1]
        j = binary_search(vec2[k:], i)
        if j == len(vec2):
            break
        if i == vec2[j][0]:
            vec.append(val*vec2[j][1])
        k = j+1
    return vec


# divide and conquer
# T(m) = 2T(m/2) + O(logn)
# worst case m * lgn
# best case ?
def multiply3(vec1, vec2):
    if not vec1 or not vec2:
        return []
    m, n = len(vec1), len(vec2)
    i = m / 2
    j = binary_search(vec2, vec1[i][0])
    element = None
    if j != n and vec1[i][0] == vec2[j][0]:
        element = (vec1[i][0], vec1[i][1]*vec2[j][1])
    return multiply3(vec1[:i], vec2[:j]) + [element] + multiply3(vec1[i+1:], vec2[j+1:])



