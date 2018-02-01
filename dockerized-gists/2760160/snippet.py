class Graph:
    
    def __init__(self, n):
        self.n = n
        self.adjs = []
        self.edges = set()
        for i in range(n):
            self.adjs.append(set())
        
    def add_edge(self, v, w):
        if v == w:
            raise Exception("Cannot create loop edge in node %s" % v)
        self.adjs[v].add(w)
        self.adjs[w].add(v)
        if not (w,v) in self.edges:
            self.edges.add((v,w))
    
    def adj(self, v, w):
        return v in self.adjs[w]
        
    def get_clique_cover(self):
        return Graph.CliqueCoverCalculator(self).calculate()
    
    # See http://citeseerx.ist.psu.edu/viewdoc/download;jsessionid=756229C2CFB6112593F593DF6D1013CF?doi=10.1.1.103.7486&rep=rep1&type=pdf
    class CliqueCoverCalculator:
        def __init__(self, g):
            self.g = g
            
        def calculate(self):
            g = self.g
            cover = []
            
            # Loop invariant: C1...Ck cover all edges incident to vertices v,w <= i
            for i in range(g.n):
            
                # W contains the nodes j before i for which edges i,j need to be covered
                w = set([j for j in range(i) if g.adj(i,j)])
                self.debug("\ni=%s; W=%s; cover=%s" % (i, w, cover))
                
                # If there are no nodes before i adjacent to it, create a new clique with i
                if len(w) == 0:
                    cover.append([i])
                    self.debug(" Creating new clique from %s" % [i])
                
                # Try to add i to each of the existing cliques
                else:
                    # Remove from W neighbors j of i where {i, j} is already covered by a previous clique
                    for clique in cover:
                        if self.can_include(i, clique):
                            clique.append(i)
                            for j in clique:
                                if j in w: w.remove(j)
                            self.debug(" Adding %s to clique %s, W is now %s" % (i, clique, w))
                            if len(w) == 0: break
                                
                    # For the remaining edges, try to cover as many as possible at a time
                    while len(w) > 0:
                        maximal_clique = self.find_maximal_clique(cover, w)
                        new_clique = [j for j in maximal_clique if j in w]
                        new_clique.append(i)
                        cover.append(new_clique)
                        for j in maximal_clique: 
                            if j in w: w.remove(j)
                        self.debug(" Generated new clique %s, W is now %s" % (new_clique, w))
            
            self.check_valid(cover)
            return cover
        
        def can_include(self, node, clique):
            return all([self.g.adj(node, k) for k in clique])

        def find_maximal_clique(self, cover, w):
            maximal = None
            value = 0
            for clique in cover:
                intersection = [j for j in clique if j in w]
                if value < len(intersection):
                    maximal, value = clique, len(intersection)
            return maximal
        
        def check_valid(self, cover):
            for v,w in self.g.edges:
                if not any([(v in clique and w in clique) for clique in cover]):
                    raise Exception("Edge %s,%s is not present in cover %s" % (v,w,cover))
                    
            for clique in cover:
                for v in clique:
                    if not all([self.g.adj(v,w) for w in clique if v != w]):
                        raise Exception("Node %s is not adjacent to all nodes in clique %s" % (v, clique))
        
            
        def debug(self, str):
            print str
            
if __name__ == "__main__":
    g = Graph(4)
    g.add_edge(0,1)
    g.add_edge(1,2)
    g.add_edge(1,3)
    g.add_edge(2,3)
    g.add_edge(0,2)
    
    cover = g.get_clique_cover()
    print "\nCover is:"
    for c in cover: print c