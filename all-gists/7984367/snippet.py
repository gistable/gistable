import numpy as np
from collections import Counter


def transport(supply, demand, costs):

    # Only solves balanced problem
    assert sum(supply) == sum(demand)

    s = np.copy(supply)
    d = np.copy(demand)
    C = np.copy(costs)

    n, m = C.shape

    # Finding initial solution
    X = np.zeros((n, m))
    indices = [(i, j) for i in range(n) for j in range(m)]
    xs = sorted(zip(indices, C.flatten()), key=lambda (a, b): b)

    # Iterating C elements in increasing order
    for (i, j), _ in xs:
        if d[j] == 0:
            continue
        else:
            # Reserving supplies in a greedy way
            remains = s[i] - d[j] if s[i] >= d[j] else 0
            grabbed = s[i] - remains
            X[i, j] = grabbed
            s[i] = remains
            d[j] -= grabbed

    # Finding optimal solution
    while True:
        u = np.array([np.nan]*n)
        v = np.array([np.nan]*m)
        S = np.zeros((n, m))

        _x, _y = np.where(X > 0)
        nonzero = zip(_x, _y)
        f = nonzero[0][0]
        u[f] = 0

        # Finding u, v potentials
        while any(np.isnan(u)) or any(np.isnan(v)):
            for i, j in nonzero:
                if np.isnan(u[i]) and not np.isnan(v[j]):
                    u[i] = C[i, j] - v[j]
                elif not np.isnan(u[i]) and np.isnan(v[j]):
                    v[j] = C[i, j] - u[i]
                else:
                    continue

        # Finding S-matrix
        for i in range(n):
            for j in range(m):
                S[i, j] = C[i, j] - u[i] - v[j]

        # Stop condition
        s = np.min(S)
        if s >= 0:
            break

        i, j = np.argwhere(S == s)[0]
        start = (i, j)

        # Finding cycle elements
        T = np.copy(X)
        T[start] = 1  
        while True:
            _xs, _ys = np.nonzero(T)
            xcount, ycount = Counter(_xs), Counter(_ys)

            for x, count in xcount.items():
                if count <= 1:
                    T[x,:] = 0
            for y, count in ycount.items():
                if count <= 1: 
                    T[:,y] = 0

            if all(x > 1 for x in xcount.values()) \
                    and all(y > 1 for y in ycount.values()):
                break
        
        # Finding cycle chain order
        dist = lambda (x1, y1), (x2, y2): abs(x1-x2) + abs(y1-y2)
        fringe = set(tuple(p) for p in np.argwhere(T > 0))

        size = len(fringe)

        path = [start]
        while len(path) < size:
            last = path[-1]
            if last in fringe:
                fringe.remove(last)
            next = min(fringe, key=lambda (x, y): dist(last, (x, y)))
            path.append(next)

        # Improving solution on cycle elements
        neg = path[1::2]
        pos = path[::2]
        q = min(X[zip(*neg)])
        X[zip(*neg)] -= q
        X[zip(*pos)] += q

    return X, np.sum(X*C)


if __name__ == '__main__':
    supply = np.array([200, 350, 300])
    demand = np.array([270, 130, 190, 150, 110])

    costs = np.array([[24., 50., 55., 27., 16.],
                      [50., 40., 23., 17., 21.],
                      [35., 59., 55., 27., 41.]])

    routes, z = transport(supply, demand, costs)
    assert z == 23540

    print routes