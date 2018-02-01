# gap.py
# (c) 2013 Mikael Vejdemo-Johansson
# BSD License
#
# SciPy function to compute the gap statistic for evaluating k-means clustering.
# Gap statistic defined in
# Tibshirani, Walther, Hastie:
#  Estimating the number of clusters in a data set via the gap statistic
#  J. R. Statist. Soc. B (2001) 63, Part 2, pp 411-423

import scipy
import scipy.cluster.vq
import scipy.spatial.distance
dst = scipy.spatial.distance.euclidean

def gap(data, refs=None, nrefs=20, ks=range(1,11)):
    """
    Compute the Gap statistic for an nxm dataset in data.

    Either give a precomputed set of reference distributions in refs as an (n,m,k) scipy array,
    or state the number k of reference distributions in nrefs for automatic generation with a
    uniformed distribution within the bounding box of data.

    Give the list of k-values for which you want to compute the statistic in ks.
    """
    shape = data.shape
    if refs==None:
  tops = data.max(axis=0)
	bots = data.min(axis=0)
	dists = scipy.matrix(scipy.diag(tops-bots))
	

	rands = scipy.random.random_sample(size=(shape[0],shape[1],nrefs))
	for i in range(nrefs):
	    rands[:,:,i] = rands[:,:,i]*dists+bots
    else:
	rands = refs

    gaps = scipy.zeros((len(ks),))
    for (i,k) in enumerate(ks):
	(kmc,kml) = scipy.cluster.vq.kmeans2(data, k)
	disp = sum([dst(data[m,:],kmc[kml[m],:]) for m in range(shape[0])])

	refdisps = scipy.zeros((rands.shape[2],))
	for j in range(rands.shape[2]):
	    (kmc,kml) = scipy.cluster.vq.kmeans2(rands[:,:,j], k)
	    refdisps[j] = sum([dst(rands[m,:,j],kmc[kml[m],:]) for m in range(shape[0])])
	gaps[i] = scipy.log(scipy.mean(refdisps))-scipy.log(disp)
    return gaps

