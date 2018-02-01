from timeit import Timer

def uniq(a):
    l = []
    [l.append(i)    for i in a    if i not in l]
    return l

def intersect(a, b):
    return [i    for i in a    if i in b]

def union(a, b):
    return uniq(a.__add__(b))

def find_group(a, b):
    l = union(a, b)
    li = l.index
    for i in l:
        if i == []:
            continue
        lx = li(i)
        for j in l[lx+1:]:
            if j == []:
                continue
            ly = li(j)
            if intersect(i, j) != []:
                l[lx] = union(i, j)
                i = l[lx]
                l[ly] = []
    return [i    for i in l    if i != []]

def test():
    a = [[1, 2, 3], [0], [3, 5], [6, 7, 8, 9], [0, 10], [1]]
    b = [[3, 11], [0, 13, 10], [18, 19], [10, 10], [1]]
    find_group(a, b)

if __name__ == "__main__":
    print Timer(test).repeat(repeat=5, number=100)