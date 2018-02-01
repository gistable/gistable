from sys import argv
import re

# open the file and get read to read data
file = open(argv[1], "r");
p = re.compile("\d+");

# initialize the graph
vertices, edges = map(int, p.findall(file.readline()))
graph = [[0]*vertices for _ in range(vertices)]

# populate the graph
for i in range(edges):
    u, v, weight = map(int, p.findall(file.readline()))
    graph[u][v] = weight
    graph[v][u] = weight

# initialize the MST and the set X
T = set();
X = set();

# select an arbitrary vertex to begin with
X.add(0);

while len(X) != vertices:
    crossing = set();
    # for each element x in X, add the edge (x, k) to crossing if
    # k is not in X
    for x in X:
        for k in range(vertices):
            if k not in X and graph[x][k] != 0:
                crossing.add((x, k))
    # find the edge with the smallest weight in crossing
    edge = sorted(crossing, key=lambda e:graph[e[0]][e[1]])[0];
    # add this edge to T
    T.add(edge)
    # add the new vertex to X
    X.add(edge[1])

# print the edges of the MST
for edge in T:
    print edge
