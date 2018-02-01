from heapq import heappush, heappop

def dijkstra(N, S, edges):
    d = [INF for i in range(N)]
    d[S] = 0
    h = []
    heappush(h, (0, S))
    for i in range(N - 1):
        min_dist, k = 0, 0
        if not h: break
        while h:
            min_dist, k = heappop(h)
            if min_dist == d[k]: break
        for j, w in edges[k]:
            if d[j] > d[k] + w:
                d[j] = d[k] + w
                heappush(h, (d[j], j))
    return d
