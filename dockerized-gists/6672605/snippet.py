# graph
# Python object that creates an ordered GraphSON representation.
#
# Author:   Benjamin Bengfort <ben@cobrain.com>
# Created:  Mon Sep 23 11:30:05 2013 -0400
#
# Copyright (C) 2013 Cobrain Company
# For license information, see LICENSE.txt
#
# ID: graph.py [] ben@cobrain.com $

"""
A Python object that exposes GraphJSON as a pythonic datastructure.

GraphSON is the ETL mechanism of choice for Titan graph databases using
Cassandra. However, the GraphSON must be ordered correctly in order to
correctly load the data using StringIO methodologies in Java. Therefore
the simple construction of a Python dictionary to hold the graph data is
not sufficient.

This class wraps the `collections.OrderedDict` to ensure order is
preserved, then wraps `json.dump` to provide output to files or writing to
a string.

Additionally, this object supports further validation of the dictionaries
that should be added as edges or vertices to ensure that the GraphSON is
constructed properly, and during LONG ETL times, it doesn't break.
"""

##########################################################################
## Imports
##########################################################################

import json
from collections import OrderedDict

##########################################################################
## Exceptions
##########################################################################

class ValidationError(Exception):
    """
    A vertex or an edge is not valid for inclusion in the graph.
    """
    pass

##########################################################################
## GraphSON object
##########################################################################

class GraphSON(object):
    """
    An ordered data structure for maintaining a GraphSON object, and the
    ability to correctly write that ordered structure to a string or to a
    file.

    :todo: Implement read functionality.
    """

    def __init__(self, vertices=[], edges=[], mode="NORMAL"):
        self._data = self._create_structure()
        self._data['graph']['mode'] = mode

        for vertex in vertices:
            self.add_vertex(vertex)

        for edge in edges:
            self.add_edge(edge)

    ##////////////////////////////////////////////////////////////////////
    ## Instance properties
    ##////////////////////////////////////////////////////////////////////

    @property
    def vertices(self):
        """
        Read only generator access to the vertices list.
        """
        for vertex in self._data['graph']['vertices']:
            yield vertex

    @property
    def edges(self):
        """
        Read only generator access to the edges list.
        """
        for edge in self._data['graph']['edges']:
            yield edge

    ##////////////////////////////////////////////////////////////////////
    ## Internal helper methods
    ##////////////////////////////////////////////////////////////////////

    def _create_structure(self):
        """
        An internal helper method for creating the wrapped `OrderedDict`
        correctly, and to create the graph structure on demand.
        """
        graph = OrderedDict([('mode',     None),
                             ('vertices', []),
                             ('edges',    [])])
        return OrderedDict([('graph', graph)])

    def _validate_vertex(self, vertex):
        """
        Ensures that a vertex object is correctly structured.
        """
        keys = ('_id', '_type')
        for key in keys:
            if key not in vertex:
                raise ValidationError("Required key '%s' not in vertex.") % key

        if vertex['_type'] != 'vertex':
            raise ValidationError("The required type 'vertex' does not match '%s'" % vertex['_type'])

        if vertex['_id'] in [v['_id'] for v in self.vertices]:
            raise ValidationError("_id '%s' is already in vertices." % str(vertex['_id']))

    def _validate_edge(self, edge):
        """
        Ensures that an edge object is correctly structured.
        """
        keys = ('_id', '_type', '_label', '_inV', '_outV')
        for key in keys:
            if key not in edge:
                raise ValidationError("Required key '%s' not in edge.") % key

        if edge['_type'] != 'edge':
            raise ValidationError("The required type 'edge' does not match '%s'" % edge['_type'])

        if edge['_id'] in [e['_id'] for e in self.edges]:
            raise ValidationError("_id '%s' is already in edges." % str(edge['_id']))

        if edge['_inV'] not in [v['_id'] for v in self.vertices]:
            raise ValidationError("No vertex for in direction in vertices list with id '%s'" % str(edge['_inV']))

        if edge['_outV'] not in [v['_id'] for v in self.vertices]:
            raise ValidationError("No vertex for out direction in vertices list with id '%s'" % str(edge['_outV']))

    ##////////////////////////////////////////////////////////////////////
    ## Publically exposed API methods
    ##////////////////////////////////////////////////////////////////////

    def clear(self):
        """
        Resets the graph and clears out any vertices and edges.
        """
        self._data = self._create_structure()

    def add_vertex(self, vertex, force=False):
        """
        Append a vertex to the GraphSON. This method will also validate
        the vertex and raise an exception, unless the force parameter is
        set to True.

        :param vertex: A dictionary containing _id and _type as well as
            any other arbitrary properties for the vertex.
        :param force: A boolean that determines whether or not to validate
            the vertex on the Graph.
        """
        if not force:
            self._validate_vertex(vertex)
        self._data['graph']['vertices'].append(vertex)

    def add_edge(self, edge, force=False):
        """
        Append an edge to the GraphSON. This method will also validate the
        edge and raise an exception, unless the force parameter is set to
        True.

        :param edge: A dictionary containing _id and _type as well as edge
            properties, _outV, _inV, and _label. Can also contain other
            arbitrary properties for the edge.
        :param force: A boolean that determines whether or not to validate
            the edge on the Graph.
        """
        if not force:
            self._validate_edge(edge)
        self._data['graph']['edges'].append(edge)

    ##////////////////////////////////////////////////////////////////////
    ## Representation methods
    ##////////////////////////////////////////////////////////////////////

    def dump(self, fp, **options):
        """
        Wrapper for `json.dump` to dump the ordered dict to JSON

        :param fp: File pointer or stream to write the JSON to.
        :param options: Keyword options passed to `json.dump`
        """
        return json.dump(self._data, fp, **options)

    def dumps(self, **options):
        """
        Wrapper for `json.dumps` to dump the ordered dict to a JSON string.

        :param options: Keyword options passed to `json.dumps`
        """
        return json.dumps(self._data, **options)

    def __str__(self):
        """
        Dumps the graph to a string with no indentation.
        """
        return self.dumps()

##########################################################################
## Main Method and Testing
##########################################################################

if __name__ == "__main__":
    g = GraphSON()
    g.add_vertex({"_id": 1, "name": "Under Armour", "_type":"vertex", "class":"vendor"})
    g.add_vertex({"_id": 2, "name": "UA Men's Tech Shorts", "gender": "M", "_type":"vertex", "class":"product"})
    g.add_edge({"_id": 1, "_type": "edge", "_label": "sells", "_outV": 1, "_inV": 2})

    print g.dumps(indent=4)
