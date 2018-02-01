def get_sparse_adjacency_matrix(G, attr=None):
  if attr:
    source, target, data = zip(*[(e.source, e.target, e[attr]) 
      for e in G.es if not np.isnan(e[attr])]);
  else:
    source, target = zip(*[(e.source, e.target) 
      for e in G.es]);
    data = np.ones(len(source)).astype('int').tolist();
  if not G.is_directed():
    # If not directed, also create the other edge
    source, target = source + target, target + source;
    data = data + data;
  L = sparse.coo_matrix((data, (source, target)), shape=[G.vcount(), G.vcount()]);
  return L;  