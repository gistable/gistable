#!/usr/bin/env python
from py2neo import neo4j
import sys
import logging
import argparse
from inspect import getmembers
from pprint import pprint

parser = argparse.ArgumentParser()
parser.add_argument("acc1",
                    help="First NCBI ID.")
parser.add_argument("acc2",
                    help="Second NCBI ID.")

opts=parser.parse_args()

logging.basicConfig(level=logging.INFO)

db = neo4j.GraphDatabaseService()

# Over this value we consider
max_distance = 1000

def get_distance_node( node1, node2, link='has_parent' ):
	query = neo4j.CypherQuery(db, "START n=node("+str(node1)+"), m=node("+str(node2)+") MATCH p=shortestPath(n-[*]-m) RETURN length(relationships(p)) as distance")

	# Dummy distance... too big
	distance = 100
	for record in query.stream():
		distance = record[0]

	return distance

def get_parent_node( node, link='has_parent' ):
	query = neo4j.CypherQuery(db, "START n=node("+str(node)+") MATCH (n-[]->(m:TAXID)) RETURN m")

	parent = 0
	
	for record in query.stream():
		parent = record[0]._id
		print "ID: "+str(parent)
		
	return parent

def parent_distance_node( node1, node2, link='has_parent' ):
	parent1 = get_parent_node( node1, link )
	distance = get_distance_node( parent1, node2, link )
	return distance


def crawler_distance_node( node1, node2 ):

	print "ITER"
	linktype = 'has_parent'
	distance = get_distance_node( node1, node2, linktype )
	
	print "DISTANCE: "+str(distance)
	
	if ( distance > max_distance ) :
		return 0
	else :
		if ( distance == 0 ):
			#print "EQUAL: "+node1
			return node1
		elif ( distance == 1 ):
			
			print get_parent_node(node1, linktype)
			print get_parent_node(node2, linktype)
			
			if ( node2 == get_parent_node(node1, linktype) ):
				#print "PARENT2: "+str(node2)
				return node2
			elif ( node1 == get_parent_node(node2, linktype) ):
				#print "PARENT1: "+str(node1)
				return node1
			else :
				return 0
		else:
			if ( parent_distance_node(node1, node2, linktype) >= distance ):
				parent2 = get_parent_node(node2, linktype)
				return crawler_distance_node( node1, parent2 )
				
			else :
				parent1 = get_parent_node(node1, linktype)
				return crawler_distance_node( parent1, node2 )




if ( opts.acc1 == opts.acc2 ):
	sys.exit("The same codes!")


TAXID = db.get_or_create_index(neo4j.Node, "TAXID")
node1list = TAXID.get("id", opts.acc1)
node2list = TAXID.get("id", opts.acc2)

node1 = 0
node2 = 0

pprint(node1list)
pprint(node2list)

for match in node1list:
	node1 = match._id

for match in node2list:
	node2 = match._id

print node1
print node2

#print get_distance_node( node1, node2 )

nodecommon = crawler_distance_node( node1, node2 )
if nodecommon == 0:
	print "No match!"
else:
	tmp = db.node(nodecommon)
	props = tmp.get_properties()
	print props['id']
