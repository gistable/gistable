
import numpy as np
import matplotlib.pyplot as plt
import sys

def main():
	if len(sys.argv) == 1 or "-h" in sys.argv or "--help" in sys.argv:
		print "python lagrange.py <x1.y1> .. <x_k.y_k>"
		print "Example:"
		print "python lagrange.py 0.1 2.4 4.5 3.2"
		exit()
	points = []
	for i in xrange(len(sys.argv)): 
		if i != 0: 
			points.append((int(sys.argv[i].split(".")[0]),int(sys.argv[i].split(".")[1]))) 

	#points =[(0,0),(25,30),(50,10), (57,0)]
	P = lagrange(points)
	nr = 2
	print "(" + str(points[nr][0]) + ", " + str(points[nr][1]) +") P(" + str(points[nr][0]) +")= " +str(P(points[nr][0]))
	plot(P, points)

def plot(f, points):
	x = range(-10, 100)
	y = map(f, x)
	print y
	plt.plot( x, y, linewidth=2.0)
	x_list = []
	y_list = []
	for x_p, y_p in points:
		x_list.append(x_p)
		y_list.append(y_p)
	print x_list
	print y_list
	plt.plot(x_list, y_list,  'ro')

	plt.show()


def lagrange(points):
	def P(x):
		total = 0
		n = len(points)
		for i in xrange(n):
			xi, yi = points[i]
			
			def g(i, n):
				
				tot_mul = 1
				for j in xrange(n):
					if i == j:
						continue
					xj, yj = points[j]
					tot_mul *= (x - xj) / float(xi - xj)
					
				return tot_mul 

			total += yi * g(i, n)
		return total
	return P 


if __name__ == "__main__":
	main()