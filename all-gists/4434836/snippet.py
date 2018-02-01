#!/usr/bin/python

def dfs(buf, flag, nodes, start, cur):
    if flag[cur]:
        if cur == start and len(nodes) != 2 and min(nodes) == start:
            return len(nodes)
        else:
            return -1
    flag[cur] = True
    nodes.append(cur)
    for adj in buf[cur]:
        ret = dfs(buf, flag, nodes, start, adj)
        if ret > 0:
            return ret
    nodes.pop()
    flag[cur] = False
    return -1

def get_cactus(buf):
    n = len(buf)
    ret = 1
    for i in xrange(n):
        flag = [False] * n
        nodes = []
        tmp = dfs(buf, flag, nodes, i, i)
        if tmp > 0:
            ret *= tmp
    return ret

def main():
    edges = [[1,2], [0,3], [0,3], [1,2,6,7], [6], [6], [3,4,5,7], [3,6]]
    ret = get_cactus(edges)
    print ret

if __name__ == '__main__':
    main()
