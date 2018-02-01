from __future__ import division
import random

# K-Means Clustering

def distance(a, b):
	""" Euclidean distance """
	return sum([(a[i]-b[i])**2 for i in range(len(a))])**0.5

class Point:

	""" Point object has coordinates (x,y,z,...) and an optional label """

	def __init__(self, coordinates, label=-1):
		self.coord = coordinates
		self.label = label

	def dist(self, other):
		return distance(self.coord, other.coord)

	def __str__(self):
		return 'Point(%s,%s)'%(self.coord, self.label)

class Cluster:

	""" Cluster object has a list of points and a calculated centroid (point) """

	def __init__(self, points):
		self.points = points
		self.center = self._calcCenter()

	def update(self, points):
		self.points = points
		self.center = self._calcCenter()

	def _calcCenter(self):
		x = [i for i in self.points[0].coord]
		for p in self.points[1:]:
			for j in range(len(p.coord)):
				x[j] += p.coord[j]
		M = len(self.points)
		return Point([xx/M for xx in x], label='center')

def kmeans(points, k, max_iter=1000, min_shift_frac=0.01):

	# initialize
	clusters = []
	for p in random.sample(points, k):
		clusters.append(Cluster([p]))

	# iterate
	this_iter = 0
	while this_iter < max_iter:
		this_iter += 1
		lists = [[] for c in range(k)]
		shifts = 0
		for p in points:
			dx = min([(p.dist(clusters[h].center), h) for h in range(k)])[1]
			if dx != p.label: shifts += 1
			p.label = dx
			lists[dx].append(p)
		for i in range(k):
			clusters[i].update(lists[i])

		# stopping condition: if %points changing clusters below thresh...
		if shifts/len(points) < min_shift_frac:
			break

	return (clusters, this_iter)
              
if __name__ == '__main__':

	import pylab, numpy, time

	points = []
	for i in range(10000):
		points.append(Point(numpy.random.random(2)))

	k = 8
	start = time.time()
	clusters, num_iters = kmeans(points, k)
	print time.time() - start

	x = [clusters[i].center.coord[0] for i in range(k)]
	y = [clusters[i].center.coord[1] for i in range(k)]
	pylab.plot(x, y, 'ko')
	for cluster in clusters:
		x = [p.coord[0] for p in cluster.points]
		y = [p.coord[1] for p in cluster.points]
		pylab.plot(x, y, '+')   
	pylab.show()