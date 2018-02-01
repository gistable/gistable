# Compute the Lovasz, Schrijver, and Szegedy numbers for graphs.
#
# A graph with 32 vertices takes under one second, so it's not the fastest.
# Probably the specialized code for Lovasz number from
#   http://dollar.biz.uiowa.edu/~sburer/pmwiki/pmwiki.php%3Fn=Main.SDPLR%3Faction=logout.html
# would be much faster (I haven't tried it).

# Copyright (c) 2013 Daniel Stahlke (dan@stahlke.org)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import print_function

import numpy as np
import cvxopt.base
import cvxopt.solvers

def parse_graph(G, complement=False):
    '''
    Takes a Sage graph, networkx graph, or adjacency matrix as argument, and returns
    vertex count and edge list for the graph and its complement.
    '''

    if type(G).__module__+'.'+type(G).__name__ == 'networkx.classes.graph.Graph':
        import networkx
        G = networkx.convert_node_labels_to_integers(G)
        nv = len(G)
        edges = [ (i,j) for (i,j) in G.edges() if i != j ]
        c_edges = [ (i,j) for (i,j) in networkx.complement(G).edges() if i != j ]
    else:
        if type(G).__module__+'.'+type(G).__name__ == 'sage.graphs.graph.Graph':
            G = G.adjacency_matrix().numpy()

        G = np.array(G)

        nv = G.shape[0]
        assert len(G.shape) == 2 and G.shape[1] == nv
        assert np.all(G == G.T)

        edges   = [ (j,i) for i in range(nv) for j in range(i) if G[i,j] ]
        c_edges = [ (j,i) for i in range(nv) for j in range(i) if not G[i,j] ]

    for (i,j) in edges:
        assert i < j
    for (i,j) in c_edges:
        assert i < j

    if complement:
        (edges, c_edges) = (c_edges, edges)

    return (nv, edges, c_edges)

def lovasz_theta(G, long_return=False, complement=False):
    '''
    Computes the Lovasz theta number for a graph.
    Takes either a Sage graph or an adjacency matrix as argument.

    If the `long_return` flag is set, returns also the optimal B and Z matrices for the primal
    and dual programs.

    >>> import networkx
    >>> G = networkx.cycle_graph(5)
    >>> abs(np.sqrt(5) - lovasz_theta(G)) < 1e-9
    True

    >>> # Vertices are {0,1}^5, edges between vertices with Hamming distance at most 2.
    >>> H = [[ 1 if bin(i ^ j).count("1") <= 2 else 0 for i in range(32) ] for j in range(32) ]
    >>> abs(16.0/3 - lovasz_theta(H)) < 1e-9
    True

    >>> Hc = np.logical_not(np.array(H))
    >>> abs(6.0 - lovasz_theta(Hc)) < 1e-9
    True
    '''

    (nv, edges, _) = parse_graph(G, complement)
    ne = len(edges)

    # This case needs to be handled specially.
    if nv == 1:
        return 1.0

    c = cvxopt.matrix([0.0]*ne + [1.0])
    G1 = cvxopt.spmatrix(0, [], [], (nv*nv, ne+1))
    for (k, (i, j)) in enumerate(edges):
        G1[i*nv+j, k] = 1
        G1[j*nv+i, k] = 1
    for i in range(nv):
        G1[i*nv+i, ne] = 1

    G1 = -G1
    h1 = -cvxopt.matrix(1.0, (nv, nv))

    sol = cvxopt.solvers.sdp(c, Gs=[G1], hs=[h1])

    if long_return:
        theta = sol['x'][ne]
        Z = np.array(sol['ss'][0])
        B = np.array(sol['zs'][0])
        return { 'theta': theta, 'Z': Z, 'B': B }
    else:
        return sol['x'][ne]

def schrijver_theta(G, long_return=False, complement=False):
    '''
    Computes the Schrijver theta^- number for a graph.
    Takes either a Sage graph or an adjacency matrix as argument.

    If the `long_return` flag is set, returns also the optimal B and Z matrices for the primal
    and dual programs.

    >>> import networkx
    >>> G = networkx.cycle_graph(5)
    >>> abs(np.sqrt(5) - schrijver_theta(G)) < 1e-9
    True

    >>> # Vertices are {0,1}^5, edges between vertices with Hamming distance at most 2.
    >>> H = [[ 1 if bin(i ^ j).count("1") <= 2 else 0 for i in range(32) ] for j in range(32) ]
    >>> abs(4 - schrijver_theta(H)) < 1e-9
    True

    >>> Hc = np.logical_not(np.array(H))
    >>> abs(6.0 - schrijver_theta(Hc)) < 1e-9
    True
    '''

    (nv, G_edges, Gc_edges) = parse_graph(G, complement)

    neG  = len(G_edges)
    neGc = len(Gc_edges)

    # This case needs to be handled specially.
    if nv == 1:
        return 1.0

    assert neG + neGc == nv*(nv-1) // 2

    c = cvxopt.matrix([0.0]*(neG+neGc) + [1.0])
    clen = neG+neGc+1

    G0 = cvxopt.spmatrix(0, [], [], (neGc, clen))
    for i in range(neGc):
        G0[i, i] = 1
    h0 = cvxopt.matrix(0.0, (neGc, 1))

    G1 = cvxopt.spmatrix(0, [], [], (nv*nv, clen))
    k = 0
    for (i, j) in Gc_edges:
        G1[i*nv+j, k] = 1
        G1[j*nv+i, k] = 1
        k += 1
    for (i, j) in G_edges:
        G1[i*nv+j, k] = 1
        G1[j*nv+i, k] = 1
        k += 1
    for i in range(nv):
        G1[i*nv+i, k] = 1
    k += 1
    assert k == clen

    G1 = -G1
    h1 = -cvxopt.matrix(1.0, (nv, nv))

    sol = cvxopt.solvers.sdp(c, Gl=G0, hl=h0, Gs=[G1], hs=[h1])

    if long_return:
        theta = sol['x'][clen-1]
        Z = np.array(sol['ss'][0])
        B = np.array(sol['zs'][0])
        return { 'theta': theta, 'Z': Z, 'B': B }
    else:
        return sol['x'][clen-1]

def szegedy_theta(G, long_return=False, complement=False):
    '''
    Computes the Szegedy theta^+ number for a graph.
    Takes either a Sage graph or an adjacency matrix as argument.

    If the `long_return` flag is set, returns also the optimal B and Z matrices for the primal
    and dual programs.

    >>> import networkx
    >>> G = networkx.cycle_graph(5)
    >>> abs(np.sqrt(5) - szegedy_theta(G)) < 1e-9
    True

    >>> # Vertices are {0,1}^5, edges between vertices with Hamming distance at most 2.
    >>> H = [[ 1 if bin(i ^ j).count("1") <= 2 else 0 for i in range(32) ] for j in range(32) ]
    >>> abs(16.0/3 - szegedy_theta(H)) < 1e-9
    True

    >>> Hc = np.logical_not(np.array(H))
    >>> abs(8.0 - szegedy_theta(Hc)) < 1e-9
    True
    '''

    (nv, edges, _) = parse_graph(G, complement)
    ne = len(edges)

    # This case needs to be handled specially.
    if nv == 1:
        return 1.0

    c = cvxopt.matrix([0.0]*ne + [1.0])

    G0 = cvxopt.spmatrix(0, [], [], (ne, ne+1))
    for i in range(ne):
        G0[i, i] = -1
    h0 = cvxopt.matrix(0.0, (ne, 1))

    G1 = cvxopt.spmatrix(0, [], [], (nv*nv, ne+1))
    for (k, (i, j)) in enumerate(edges):
        G1[i*nv+j, k] = 1
        G1[j*nv+i, k] = 1
    for i in range(nv):
        G1[i*nv+i, ne] = 1

    G1 = -G1
    h1 = -cvxopt.matrix(1.0, (nv, nv))

    sol = cvxopt.solvers.sdp(c, Gl=G0, hl=h0, Gs=[G1], hs=[h1])

    if long_return:
        theta = sol['x'][ne]
        Z = np.array(sol['ss'][0])
        B = np.array(sol['zs'][0])
        return { 'theta': theta, 'Z': Z, 'B': B }
    else:
        return sol['x'][ne]

# Aliases
theta = lovasz_theta
thm = schrijver_theta
thp = szegedy_theta

# Functions on the complement of a graph
def thbar(G, long_return=False):
    return lovasz_theta(G, long_return, complement=True)
def thmbar(G, long_return=False):
    return schrijver_theta(G, long_return, complement=True)
def thpbar(G, long_return=False):
    return szegedy_theta(G, long_return, complement=True)

if __name__ == "__main__":
    print("Running doctests.")
    cvxopt.solvers.options['show_progress'] = False
    cvxopt.solvers.options['abstol'] = float(1e-10)
    cvxopt.solvers.options['reltol'] = float(1e-10)
    import doctest
    doctest.testmod()
    print('Done.')

#    def hamming(n_bits, dist_eval):
#        N = 2**n_bits
#        H = [[ 1 if dist_eval(bin(i ^ j).count("1")) else 0 for i in range(N) ] for j in range(N) ]
#        return H
#
#    n = 6
#    H = hamming(n, lambda x: x >= n//2)

#    # Test graphs from sage database (must be run from within Sage)
#    from sage.all import *;
#    for nverts in range(9):
#        Q = GraphQuery(GraphDatabase(), display_cols=['graph6','lovasz_number'], num_vertices=nverts)
#        print 'nverts:', nverts, 'cnt:', Q.number_of()
#
#        cur = Q.__database__.__connection__.cursor()
#        cur.execute(Q.__query_string__, tuple(str(s) for s in Q.__param_tuple__))
#        glist = list(cur)
#
#        for (g6, lov) in glist:
#            G = Graph(str(g6), format='graph6')
#            err = lovasz_theta(G) - lov
#            if abs(err) > 3e-6:
#                print g6, err
