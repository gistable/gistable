# Serrano, Boguna, Vespigani backbone extractor
# from http://www.pnas.org/content/106/16/6483.abstract
# Thanks to Michael Conover and Qian Zhang at Indiana with help on earlier versions
# Thanks to Clay Davis for pointing out an error

import networkx as nx
import numpy as np
from scipy import integrate

def extract_backbone(g, alpha):
  backbone_graph = nx.Graph()
  for node in g:
      k_n = len(g[node])
      if k_n > 1:
          sum_w = sum( g[node][neighbor]['weight'] for neighbor in g[node] )
          for neighbor in g[node]:
              edgeWeight = g[node][neighbor]['weight']
              pij = float(edgeWeight)/sum_w
              if (1-pij)**(k_n-1) < alpha: # equation 2
                  backbone_graph.add_edge( node,neighbor, weight = edgeWeight)
  return backbone_graph