"""
Some functions related to Bayesian networks (DAGs).

Most of this was pulled from:
    http://www.mi.parisdescartes.fr/~nuel/bntworkshop2010/lecture3.pdf

"""

import networkx as nx

__all__ = ['markov_blanket', 'moral_graph', 'maximum_spanning_tree',
           'clique_graph', 'junction_tree']

def markov_blanket(G, n):
    """
    Returns the Markov blanket of `n`.

    The Markov blanket consists of the parents of `n`, the children of `n`, and
    any other parents of the children of `n`.

    Parameters
    ----------
    G : DiGraph
        A direct acyclic graph.
    n : node
        A node in `G`.

    Returns
    -------
    blanket : set
        The Markov blanket of `n`.

    Notes
    -----
    The procedure works for any directed graph, but the interpretation of the
    result is valid only when `G` is a DAG.

    """
    blanket = set(G.pred[n])
    children = list(G.succ[n].keys())
    blanket.update(children)
    for child in children:
        blanket.update(G.pred[child])
    return blanket

def moral_graph(G):
    """
    Returns the moral graph of `G`.

    The moral graph is an undirected graph where every node in `G` is connected
    to its Markov blanket.

    Parameters
    ----------
    G : DiGraph
        A direct acyclic graph.

    Returns
    -------
    MG : Graph
        The moral graph of `G`.

    """
    MG = nx.Graph()
    for u in G:
        blanket = markov_blanket(G, u)
        MG.add_edges_from([(u, v) for v in blanket if v != u])
    return MG

def maximum_spanning_tree(G, weight='weight'):
    """
    Return a maximum spanning tree or forest of an undirected, weighted graph.

    Parameters
    ----------
    G : Graph
        An undirected, weighted graph.
    weight : str
        The attribute used as weights.

    Returns
    -------
    T : Graph
       A minimum spanning tree or forest.

    Notes
    -----
    The maximum spanning tree is unique only if every weight is unique.

    See Also
    --------
    nx.minimum_spanning_tree

    """
    # Leave the original graph untouched.
    G = G.copy()

    # Negate all the weights.
    for u, v, data in G.edges_iter(data=True):
        data[weight] = -data.get(weight, 1)

    # Build the minimum spanning tree.
    T = nx.minimum_spanning_tree(G, weight)

    # Un-negate all the weights.
    for u, v, data in T.edges_iter(data=True):
        data[weight] = -data.get(weight, 1)

    return T

### This is networkx.algorithms.clique.make_max_clique_graph but modified
### to include weights according to the intersection of the cliques.
def clique_graph(G, create_using=None, name=None):
    """Create the maximal clique graph of a graph.

    Finds the maximal cliques and treats these as nodes.
    The nodes are connected if they have common members in
    the original graph.  Theory has done a lot with clique
    graphs, but I haven't seen much on maximal clique graphs.

    Notes
    -----
    This should be the same as make_clique_bipartite followed
    by project_up, but it saves all the intermediate steps.
    """
    cliq = list(map(set, nx.find_cliques(G)))
    if create_using:
        B = create_using
        B.clear()
    else:
        B = nx.Graph()
    if name is not None:
        B.name = name

    to_node = lambda cl: tuple(sorted(cl))
    for i, cl in enumerate(cliq):
        u = to_node(cl)
        B.add_node(u)
        for j, other_cl in enumerate(cliq[:i]):
            intersect = cl & other_cl
            if intersect:     # Not empty
                B.add_edge(u, to_node(other_cl), weight=len(intersect))
    return B

def junction_tree(G):
    """Return a junction tree of `G`.

    A junction tree of `G` is a maximal weight spanning tree of the clique
    graph of `G`.  Its width is the size of the largest clique of `G` minus
    one, and is minimal.

    Parameters
    ----------
    G : Graph
        A moral graph.

    Returns
    -------
    J : Graph
        A junction tree.

    """
    CG = clique_graph(G)
    J = maximum_spanning_tree(CG)
    return J

if __name__ == '__main__':
    H = nx.DiGraph()
    H.add_edges_from([('A', 'B'), ('A', 'E'), ('B', 'D'), ('C', 'B'),
                      ('C', 'E'), ('D', 'F'), ('E', 'F'), ('E', 'G')])

    G = moral_graph(H)
    J = junction_tree(G)