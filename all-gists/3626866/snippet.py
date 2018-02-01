In [12]: l = ['a', 'a', 'c', 'c', 'c', 'b']

In [13]: u = np.unique(l)

In [14]: u
Out[14]: 
array(['a', 'b', 'c'], 
      dtype='|S1')

In [15]: np.searchsorted(u, l)
Out[15]: array([0, 0, 2, 2, 2, 1])