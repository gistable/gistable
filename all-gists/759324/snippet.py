#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pip install python-freebase
# pip install git+git://github.com/networkx/networkx.git
# need github version, as write_gexf() is not in current 
# networkx 1.3 release

import freebase as fb
import networkx as nx

def getBoardMembers(id=None, name=None):
    """Return all the board members for a company."""

    # MQL query, in the form of a Python datastructure
    qGetBoardMembers = {
        "/organization/organization/board_members": [{
            "/organization/organization_board_membership/member": {
                "name": None,
                "id": None
            }
        }],
        "id":   None,
        "name": None 
    }

    # Assign the id and/or the name/label in the query
    qGetBoardMembers['id'] = id
    qGetBoardMembers['name'] = name

    result = fb.mqlread(qGetBoardMembers)

    # construct a tuple with two dictionaries (rootnode and related nodes)
    # a node has a { id : label } form
    persons = {}

    for p in result['/organization/organization/board_members']:
        pid = p['/organization/organization_board_membership/member']['id']
        plabel = p['/organization/organization_board_membership/member']['name']
        persons[pid] = plabel

    rootnode = {result['id']: result['name']}

    return (rootnode, persons)


def getBoardMemberships(id=None, name=None):
    """Get al boardmemberships for a person."""

    qGetBoardMemberships = {
      "/business/board_member/organization_board_memberships": [{
        "/organization/organization_board_membership/organization": {
          "id":   None,
          "name": None
        }
      }],
      "id": None,
      "name": None,
      "type": "/business/board_member"
    }
    
    qGetBoardMemberships['id'] = id
    qGetBoardMemberships['name'] = name

    result = fb.mqlread(qGetBoardMemberships)
    companies = {}

    for m in result['/business/board_member/organization_board_memberships']:
        cid = m['/organization/organization_board_membership/organization']['id']
        clbl = m['/organization/organization_board_membership/organization']['name']
        companies[cid] = clbl

    rootnode = {result['id']: result['name']}

    return (rootnode, companies)


def toGraph(rootnode, nodes, invert=False):
    """Convert a graph structure from tuple-form to networkx format."""

    G = nx.DiGraph() # Directed graph

    # Add rootnode
    rootid, rootlbl = rootnode.popitem()
    G.add_node(rootid, label=rootlbl)

    # Add related nodes and edges _from_ root node
    # if inverted, edges will be _to_ root node
    for nodeid, nodelbl in nodes.iteritems():
        G.add_node(nodeid, label=nodelbl)
        if invert == False:
            G.add_edge(rootid, nodeid)
        else:
            G.add_edge(nodeid, rootid)

    return G

def mergeCompanies(companylist):
    """Create a joint networkx graph for multiple companies.

    Keyword argument is a dictionary of company nodes, e.g.
    { '\companyid' : 'name' , ... }
    """

    G = nx.DiGraph()

    for c in companylist.keys():
        data = getBoardMembers(id=c) # query on id
        cG = toGraph(*data) # unpack tuple
        G = nx.compose(G,cG) # merge in main graph, autom. deduplication
    
    return G


# There is currently no property for expressing that a company is part
# of a market index such as BEL20, otherwise we could just query
# for that
BEL20 = ["Anheuser-Busch InBev", 'Solvay', 'Delhaize Group', 'UCB', 
    'Ackermans & Van Haaren', 'Bekaert', 'Cofinimmo', 
    'Groupe Bruxelles Lambert', 'Omega Pharma', 'Umicore', 
    'Belgacom', 'Befimmo-Sicafi', 'KBC Group', 'Telenet Group Holding N.V.',
    'Colruyt', 'GDF Suez', 'Mobistar', 'NPM/CNP', 'Dexia', 'Ageas']

# Get the boardmembers of every company a boardmember of a BEL20 company is on
# (not the most efficient way...)
companydict = {}
for c in BEL20:
    cnode, pnodes = getBoardMembers(name=c)
    companydict.update(cnode)
    for p in pnodes.values():
        pnode, cnodes = getBoardMemberships(name=p)
        companydict.update(cnodes)

# Merge the data for all the companies in a single graph
G = mergeCompanies(companydict) 

# Write to the Gephi GEXF XML-format
nx.write_gexf(G, 'directorates.gexf')
