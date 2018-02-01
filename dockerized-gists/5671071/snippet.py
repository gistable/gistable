from neo4jrestclient.client import GraphDatabase
from neo4jrestclient.constants import RAW
from neo4jrestclient.client import Node 

from urlparse import urlparse
import re, json

from flask import Flask, Response, json, jsonify, request, Blueprint, render_template

app = Flask(__name__)

@app.route('/_api/hydraGraph')
def api_response():

	callbackArguments = request.args['callback']

	# create DB connection
	db = GraphDatabase("http://localhost:7475/db/data")

	nodes = getNodes(db)
	rels = getRels(db)

	result = {
		'nodes' : nodes,
		'rels' : rels
	}

	result = json.dumps(result)

	# GET Request Response
	callbackWrapper = callbackArguments + "(" + result + ")"
	resp = Response(callbackWrapper, status = 200, mimetype = 'application/json') 
	return resp 


def createNodeJSON(name, uid, description):	
	JSONObject = {
		'name': name,
		'id' : uid,
		'description' : description
	}
	return JSONObject


def createRelsJSON(startNode, endNode):
	JSONObject = {
		'startNode' : startNode,
		'endNode' : endNode
	}
	return JSONObject


def doRegEX(urlString):
	regex = re.compile("([^/]*)$")
	stripedURLComponent = regex.search(urlString.path)
	return stripedURLComponent.group(0)


def getNodes(db):
	q = "START n=node(*) RETURN n"
	params = {}
	querySquenceObject = db.query(q, params=params, returns=RAW)	
	
	#Blank list to hold the JSON
	nodeJSON = []

	# Iterating over the resposes from the graph db
	# NOTE:Excluding the ROOT NODE from RETURN!!!!
	for node in querySquenceObject[1:]:
		n = node.pop()
		data = n.get('data')
		name = data.get('name')
		description = data.get('description')

		self = n.get('self')
		print self
		self = urlparse(self)
		uid = doRegEX(self)

		nodeJSON.append(createNodeJSON(name, uid, description))
	
	return nodeJSON

def getRels(db):
	q = "START n=node(*) MATCH (n)-[r]->() RETURN r"
	params = {}
	querySquenceObject = db.query(q, params=params, returns=RAW)

	#Blank list to hold the JSON
	relsJSON = []
	
	for rel in querySquenceObject:
		r = rel.pop()
		start = r.get('start')
		end = r.get('end')
		
		start = urlparse(start)
		end = urlparse(end)
		
		startNode = doRegEX(start)
		endNode = doRegEX(end)

		relsJSON.append(createRelsJSON(startNode, endNode))
	
	return relsJSON


if __name__ == '__main__':
	app.debug = True
	app.run()
