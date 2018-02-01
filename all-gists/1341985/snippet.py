import networkx as nx
from collections import defaultdict
from itertools import combinations

def get_percolated_cliques(G, k, cliques=None):
    """
    Finds k-percolated cliques in G, e.g,

    Unless the cliques argument evaluates to True, this algorithm
    first enumerates all cliques in G. These are stored in memory,
    which in large graphs can consume large amounts of memory.
    Returns a generator object. To return a list of percolated k-cliques,
    use list(get_percolated_cliques(G, k)

    >>> G = nx.Graph()
    >>> G.add_edges_from(combinations(range(5), 2)) # Add a five clique
    >>> G.add_edges_from(combinations(range(2,7), 2)) # Add another five clique
    >>> list(get_percolated_cliques(G, 4))
    [frozenset([0, 1, 2, 3, 4, 5, 6])]
    >>> list(get_percolated_cliques(G, 5))
    []

    Notes
    -----
    Based on the method outlined in Palla et. al., Nature 435,
    814-818 (2005)

    """

    if not(cliques):
        cliques = nx.find_cliques(G)
    cliques = [frozenset(c) for c in cliques if len(c) >= k]

    # First index which nodes are in which cliques
    membership_dict = defaultdict(list)
    for clique in cliques:
        for node in clique:
            membership_dict[node].append(clique)

    # For each clique, see which adjacent cliques percolate
    perc_graph = nx.Graph()
    perc_graph.add_nodes_from(cliques)
    for clique in cliques:
        for adj_clique in get_adjacent_cliques(clique, membership_dict):
            if len(clique.intersection(adj_clique)) >= (k - 1):
                perc_graph.add_edge(clique, adj_clique)

    # Connected components of clique graph with perc edges
    # are the percolated cliques
    for component in nx.connected_components(perc_graph):
        yield(frozenset.union(*component))

def get_adjacent_cliques(clique, membership_dict):
    adjacent_cliques = set()
    for n in clique:
        for adj_clique in membership_dict[n]:
            if clique != adj_clique:
                adjacent_cliques.add(adj_clique)
    return adjacent_cliques
