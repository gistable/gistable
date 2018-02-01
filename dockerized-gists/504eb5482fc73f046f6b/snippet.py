import sys
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def plot(data,filename,degreetype):
    """ Plot Distribution """
    plt.plot(range(len(data)),data,'bo')
    plt.yscale('log')
    plt.xscale('log')
    plt.ylabel('Freq')
    plt.xlabel('Degree')
    plt.savefig(filename + '_' + degreetype + '_distribution.eps')
    plt.clf()

    """ Plot CDF """
    s = float(data.sum())
    cdf = data.cumsum(0)/s
    plt.plot(range(len(cdf)),cdf,'bo')
    plt.xscale('log')
    plt.ylim([0,1])
    plt.ylabel('CDF')
    plt.xlabel('Degree')
    plt.savefig(filename + '_' + degreetype + '_cdf.eps')
    plt.clf()

    """ Plot CCDF """
    ccdf = 1-cdf
    plt.plot(range(len(ccdf)),ccdf,'bo')
    plt.xscale('log')
    plt.yscale('log')
    plt.ylim([0,1])
    plt.ylabel('CCDF')
    plt.xlabel('Degree')
    plt.savefig(filename + '_' + degreetype + '_ccdf.eps')
    plt.clf()

edgelist_file = sys.argv[1]

""" Load graph """
G = nx.read_edgelist(edgelist_file, nodetype=int, create_using=nx.DiGraph())

""" To sparse adjacency matrix """
M = nx.to_scipy_sparse_matrix(G)

indegrees = M.sum(0).A[0]
outdegrees = M.sum(1).T.A[0]
indegree_distribution = np.bincount(indegrees)
outdegree_distribution = np.bincount(outdegrees)

plot(indegree_distribution, edgelist_file, 'indegree')
plot(outdegree_distribution, edgelist_file, 'outdegree')
