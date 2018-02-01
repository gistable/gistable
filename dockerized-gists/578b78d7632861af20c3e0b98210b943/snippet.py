'''
 Chaos Game Sierpinski Triangle 
 Reference: https://www.youtube.com/watch?v=kbKtFN71Lfs
'''
import random
import matplotlib.pyplot as plt
from numpy.random import rand
def midPoint(p1, p2):
	return ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)
	
def randomVertex(verticies):
	return random.choice(verticies)
	
verticies = [(1, 0), (0.5, 1), (0, 0)]
x,y = zip(*verticies)
plt.scatter(x,y,s=1)
initialPosition = (random.random(), random.random())
currentPosition = initialPosition
points = [initialPosition]
for i in range(0,1000000):
	# Get random vertex
	nextVertex = randomVertex(verticies)
	# Calculate next point
	nextPoint = midPoint(nextVertex, currentPosition)
	currentPosition = nextPoint
	# Add new point to array
	points.append(currentPosition)
m,n = zip(*points)
plt.scatter(m,n,s=1)
plt.show()