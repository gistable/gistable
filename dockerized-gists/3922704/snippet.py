def tarjan(N, S, T, edges):
    cnt = 0
    bridges = []
    visit = [0 for i in range(N)]
    low = [N + 1 for i in range(N)]
    ret = [False for i in range(N)]
    q = [0 for i in range(N + 1)]
    q[0] = (S, -1, -1)
    top = 0
    while top >= 0:
        i, father, v = q[top]
        if v == -1:
            ret[i] = (i == T)
            cnt = cnt + 1
            visit[i] = low[i] = cnt
        elif v < len(edges[i]):
            j, w, flag = edges[i][v]
            if flag:
                if j == q[top + 1][0]:
                    ret[i] = ret[i] or ret[j]
                    if ret[i]: low[i] = min(low[i], low[j])
        v += 1
        q[top] = (i, father, v)
        if v < len(edges[i]):
            j, w, flag = edges[i][v]
            if flag:
                if not visit[j]:
                    top += 1
                    q[top] = (j, i, -1)
            else:
                if j != father and visit[j]:
                    low[i] = min(low[i], visit[j])
        else:
            if low[i] == visit[i] and ret[i]:
                if father >=0:
                    bridges.append((father, i))
            top -= 1

    #print "visit", visit
    #print "low", low
    #print "ret", ret
    return bridges