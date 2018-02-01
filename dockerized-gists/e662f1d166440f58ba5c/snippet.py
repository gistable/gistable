# Wes Floyd April 2015

import sys
import requests
import json
import argparse
import pprint
import time

pp = pprint.PrettyPrinter(indent=4)

parser = argparse.ArgumentParser(description='Check for operation of a Storm process')
parser.add_argument('--nimbus', help='host running Nimbus server')
parser.set_defaults(nimbus='sandbox224')
parser.add_argument('--interval', help='time to wait between checks for complete topologies')
parser.set_defaults(interval=5)
args = parser.parse_args()

# Check tuples every X seconds
tupleCheckInterval = args.interval
nimbusServer = args.nimbus
nimbusPort = "8744"
url = "http://" + nimbusServer + ":" + nimbusPort + "/api/v1/topology/summary"

resp = requests.get(url)
resp.encoding = 'utf-8'
topologySummary = resp.json()

#Get most recent number of emitted tuples for that topology or 0 on error
def getTopoTuples(topoID):
    url = "http://" + nimbusServer + ":" + nimbusPort + "/api/v1/topology/"+topoID
    resp = requests.get(url)
    resp.encoding = 'utf-8'
    data = resp.json()
    
    #If the topology ID does not exist, return 0
    if 'error' in data:
        print 'Topology "'+topoID+'" returned error'
        return 0
    
    #Return number of emitted tuples for "all time"
    #Doc - https://github.com/apache/storm/blob/0.9.3-branch/STORM-UI-REST-API.md#apiv1topologyid-get
    return data['topologyStats'][3]['emitted']

#Returns a dictionary of tuple id and the number of its current emitted tuples
def updateTupleCounts(data):
    tuplesEmitted = {}
    for topology in data['topologies']:
        topologyID = topology['id']
        tuplesEmitted[topologyID] = getTopoTuples(topologyID)
    return tuplesEmitted

# Send some alert on the topology
def alertTopo(id):
    print 'Topology with id:\'' + id + 'has stopped processing tuples\''

# Prime the loop by getting the current list of tuple ids and emitted count, then wait for interval time
oldTupleCountDict = updateTupleCounts(topologySummary)
# Prime the loop by waiting the interval for the tuples to increase
time.sleep(tupleCheckInterval)
# Constantly check to see if topologies have stopped receiving tuples
while True:
    newTupleCountDict = updateTupleCounts(topologySummary)

    #iterate through oldTuple list, alert if same number of all time tuples were emitted
    for key in oldTupleCountDict:
        oldTupleID = key
        oldTupleCount = oldTupleCountDict[key]
        newTupleCount = newTupleCountDict[oldTupleID]

        # If tuple count has not increased
        if newTupleCount <= oldTupleCount:
            print "old",oldTupleCount
            print "new",newTupleCount
            alertTopo(oldTupleID)
        else:
            print 'DEBUG: "'+oldTupleID+'" continues to run properly'

    #TODO Consider removing topologies from oldTupleCountDict when alert is triggered?

    # Update oldTupleCountDict to reflect the most recent count data
    oldTupleCountDict = updateTupleCounts(topologySummary)
    # Delay loop for interval time period
    time.sleep(tupleCheckInterval)


