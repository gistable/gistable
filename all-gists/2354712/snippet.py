#!/usr/bin/env python
import random

# does nodes need to have edges?
createEdges = True
# number of nodes
nodes = 500

def main():
	for i in range(0, nodes):
		print '{\n'
		if(createEdges):
			edges(i)
		print '\n\t"data": {"$color": "#83548B","$type": "circle"},"id": "graphnode' + str(i) + '","name": "graphnode'+ str(i) +'"}',
		if (i != nodes - 1):
			print ','
		
def edges(i):
	edges = random.randint(0, 4)
	print '"adjacencies": ['
	for j in range(0, edges):
		referto = random.randint(0, nodes)
		print '{"nodeTo": "graphnode'+ str(referto) +'", "nodeFrom": "graphnode' + str(i) +'", "data": {}}',
		#print str(j) + ' ' + str(rand)
		if (j != edges -1):
			print ','
	print '],',
	

main()
