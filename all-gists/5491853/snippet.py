def path_cost(graph, path, weights=None):
    pathcost = 0
    for i in range(len(path)):
        if i > 0:
            edge=graph.es.find(_source=path[i-1], _target=path[i])
            if weights != None:
                pathcost += edge[weights]
            else:
                #just count the number of edges
                pathcost += 1
    return pathcost

def yen_igraph(graph, source, target, num_k, weights):
    import queue

    #Shortest path from the source to the target
    A = [graph.get_shortest_paths(source, to=target, weights=weights, output="vpath")[0]]
    A_costs = [path_cost(graph, A[0], weights)]

    #Initialize the heap to store the potential kth shortest path
    B = queue.PriorityQueue()

    for k in range(1, num_k):
        #The spur node ranges from the first node to the next to last node in the shortest path
        for i in range(len(A[k-1])-1):
            #Spur node is retrieved from the previous k-shortest path, k − 1
            spurNode = A[k-1][i]
            #The sequence of nodes from the source to the spur node of the previous k-shortest path
            rootPath = A[k-1][:i]

            #We store the removed edges
            removed_edges = []

            for path in A:
                if len(path) - 1 > i and rootPath == path[:i]:
                    #Remove the links that are part of the previous shortest paths which share the same root path
                    edge = graph.es.select(_source=path[i], _target=path[i+1])
                    if len(edge) == 0:
                        continue #edge already deleted
                    edge = edge[0]
                    removed_edges.append((path[i], path[i+1], edge.attributes()))
                    edge.delete()

            #Calculate the spur path from the spur node to the sink
            spurPath = graph.get_shortest_paths(spurNode, to=target, weights=weights, output="vpath")[0]

            if len(spurPath) > 0:
                #Entire path is made up of the root path and spur path
                totalPath = rootPath + spurPath
                totalPathCost = path_cost(graph, totalPath, weights)
                #Add the potential k-shortest path to the heap
                B.put((totalPathCost, totalPath))

            #Add back the edges that were removed from the graph
            for removed_edge in removed_edges:
                node_start, node_end, cost = removed_edge
                graph.add_edge(node_start, node_end)
                edge = graph.es.select(_source=node_start, _target=node_end)[0]
                edge.update_attributes(cost)

        #Sort the potential k-shortest paths by cost
        #B is already sorted
        #Add the lowest cost path becomes the k-shortest path.
        while True:
            cost_, path_ = B.get()
            if path_ not in A:
                #We found a new path to add
                A.append(path_)
                A_costs.append(cost_)
                break

    return A, A_costs