"""
Function that takes a pandas dataframe (with values like a biadjacency matrix) as input
and returns B, a weighted bipartite graph in networkx.
Assumes dataframe index and column labels are intended as node labels.
Weighted edges added for all cells > 0.
"""
import pandas as pd
import networkx as nx
from networkx.algorithms import bipartite
import matplotlib.pyplot as plt


def nx_graph_from_biadjacency_pandas_df(df):
    B = nx.Graph()
    for i in df.index:
        B.add_node(i, bipartite=0)
        for j in df.columns:
            B.add_node(j, bipartite=1)
            if (df.ix[i,j] > 0):
                B.add_edge(i, j, weight=df.ix[i,j])
    return B


# messy stuff from here down
# should get weighted edges for the projections
# have a look at some of the measures available in bipartite

df = pd.read_csv('<my_file>.csv', sep=';', header=0, index_col='<index_col_name>')

B = nx_graph_from_biadjacency_pandas_df(df)

nx.is_connected(B)
bottom_nodes, top_nodes = bipartite.sets(B)

nx.info(B)

for k in B:
    print(k)

list(bottom_nodes)

nx.draw(G1, with_labels=True)

c = bipartite.color(B)

degree = nx.degree(B)

G1 = bipartite.projected_graph(B, top_nodes)
G2 = bipartite.projected_graph(B, bottom_nodes)

nx.write_gexf(B, '<my_file1>.gexf')
nx.write_gexf(G1, 'my_file1>_G1.gexf')
nx.write_gexf(G2, 'my_file1>_G2.gexf')