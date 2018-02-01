#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Hierarchical link clustering
============================

:Author: Tamás Nepusz

This is an implementation of the hierarchical link clustering algorithm of Ahn
et al. The results provided by this implementation match those of the original
Python implementation of the authors, but it is somewhat faster.  At least I
hope so. Also, it handles all the input graph formats that igraph_ handles.

.. _igraph: http://igraph.sourceforge.net
"""

from __future__ import division
from collections import defaultdict
from igraph import load
from itertools import izip
from operator import itemgetter
from optparse import OptionParser
from textwrap import dedent

import logging
import sys


__author__ = "Tamas Nepusz"
__license__ = "MIT"
__docformat__ = "restructuredtext en"
__version__ = "0.1"


class JaccardSimilarityCalculator(object):
    """Calculates pairwise Jaccard similarities on a given unweighted
    graph. When calculating the similarities, it is assumed that every
    vertex is linked to itself.
    """

    def __init__(self, graph):
        self._adjlist = [set(graph.neighbors(i)).union([i])
                         for i in xrange(graph.vcount())]

    def get_similarity(self, v1, v2):
        """Returns the Jaccard similarity between the two given vertices,
        assuming that both of them are linked to themselves."""
        set1, set2 = self._adjlist[v1], self._adjlist[v2]
        isect = len(set1.intersection(set2))
        return isect / (len(set1) + len(set2) - isect)


class TanimotoSimilarityCalculator(object):
    """Calculates pairwise Tanimoto coefficients on a given weighted
    graph. When calculating the similarities, it is assumed that every
    vertex is linked to itself with an edge whose weight is equal to the
    average weight of edges adjacent to the vertex."""

    def __init__(self, graph, attr="weight"):
        degrees = graph.degree()
        strengths = graph.strength(weights=attr)
        weights = graph.es[attr]

        self._adjedgelist = []
        get_eid = graph.get_eid     # prelookup
        for i in xrange(graph.vcount()):
            weis = dict((j, weights[get_eid(i, j)]) for j in graph.neighbors(i))
            weis[i] = strengths[i] / degrees[i]
            self._adjedgelist.append(weis)

        self._sqsums = [sum(value * value for value in vec.itervalues())
                        for vec in self._adjedgelist]

    def get_similarity(self, v1, v2):
        """Returns the Tanimoto coefficient of the two given vertices,
        assuming that both of them are linked to themselves."""
        vec1, vec2 = self._adjedgelist[v1], self._adjedgelist[v2]

        if len(vec1) > len(vec2):
            # vec1 must always be the smaller
            vec1, vec2 = vec2, vec1

        numerator = sum(value * vec2.get(key, 0)
                        for key, value in vec1.iteritems())
        return numerator / (self._sqsums[v1] + self._sqsums[v2] - numerator)


class EdgeCluster(object):
    """Class representing a group of edges (i.e. a group of vertices
    in the line graph)

    This class also keeps track of the original vertices the edges
    refer to."""

    __slots__ = ("vertices", "edges")

    def __init__(self, vertices, edges):
        self.vertices = set(vertices)
        self.edges = set(edges)

    def is_smaller_than(self, other):
        """Compares this group of edges with another one based on
        size."""
        return len(self.edges) < len(other.edges)

    def partition_density(self):
        """Returns the number of edges times the relative density
        of this group. This value is used in the calculation of
        the overall partition density, used to select the best
        threshold."""
        m, n = len(self.edges), len(self.vertices)
        if n <= 2:
            return 0.
        return m * (m-n+1) / (n-2) / (n-1)

    def merge_from(self, other):
        """Merges another group of edges into this one, updating
        self.vertices and self.edges"""
        self.vertices |= other.vertices
        self.edges |= other.edges

    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__,
                self.vertices, self.edges)


class EdgeClustering(object):
    """Class representing an edge clustering of a graph as a whole.

    This class is essentially a list of `EdgeCluster` instances
    plus some additional bookkeeping to facilitate the easy lookup
    of the cluster of a given edge.
    """

    def __init__(self, edgelist):
        """Constructs an initial edge clustering of the given graph
        where each edge belongs to its own cluster.
        
        The graph is given by its edge list in the `edgelist`
        parameter."""
        self.clusters = [EdgeCluster(edge, (i, ))
                         for i, edge in enumerate(edgelist)]
        self.membership = range(len(edgelist))
        self.d = 0.0

    def lookup(self, edge):
        """Returns the cluster of a given edge"""
        return self.clusters[self.membership[edge]]

    def merge_edges(self, edge1, edge2):
        """Merges the clusters corresponding to the given edges."""
        cid1, cid2 = self.membership[edge1], self.membership[edge2]

        # Are they the same cluster?
        if cid1 == cid2:
            return

        cl1, cl2 = self.clusters[cid1], self.clusters[cid2]

        # We will always merge the smaller into the larger cluster
        if cl1.is_smaller_than(cl2):
            cl1, cl2 = cl2, cl1
            cid1, cid2 = cid2, cid1

        # Save the partition densities
        dc1, dc2 = cl1.partition_density(), cl2.partition_density()

        # Merge the smaller cluster into the larger one
        for edge in cl2.edges:
            self.membership[edge] = cid1
        cl1.merge_from(cl2)
        self.clusters[cid2] = cl1

        # Update D
        self.d += cl1.partition_density() - dc1 - dc2

    def partition_density(self):
        """Returns the overall partition density of the clustering."""
        return self.d * 2.0 / len(self.membership)


class HLC(object):
    """Hierarchical link clustering algorithm on a given graph.

    This class implements the algorithm outlined in Ahn et al: Link communities
    reveal multiscale complexity in networks, Nature, 2010. 10.1038/nature09182

    The implementation supports undirected and unweighted networks only at the
    moment, and it is assumed that the graph does not contain multiple or loop
    edges. This is not ensured within the class for sake of efficiency.

    The class provides the following attributes:

    - `graph` contains the graph being analysed
    - `min_size` contains the minimum size of the clusters one is interested
      in. It is advised to set this to at least 3 (which is the default value)
      to ensure that pseudo-clusters containing only two nodes do not turn up
      in the results.

    The algorithm may be run with or without a similarity threshold. When no
    similarity threshold is passed to the `run()` method, the algorithm will
    scan over the possible range of similarities and return a partition that
    corresponds to the similarity with the highest partition density. In this
    case, the similarity threshold and the partition density is recorded in
    the `last_threshold` and `last_partition_density` attributes. The former
    is also set properly when a single similarity threshold is used.
    """

    def __init__(self, graph = None, min_size = 3):
        """Constructs an instance of the algorithm. The algorithm
        will be run on the given `graph` with the given minimum
        community size `min_size`."""
        self._graph = None
        self._edgelist = None
        self.last_threshold = None
        self.last_partition_density = None
        self.graph = graph
        self.min_size = int(min_size)

    @property
    def graph(self):
        """Returns the graph being clustered."""
        return self._graph

    @graph.setter
    def graph(self, graph):
        """Sets the graph being clustered."""
        self._graph = graph
        self._edgelist = graph.get_edgelist()

    def run(self, threshold = None):
        """Runs the hierarchical link clustering algorithm on the
        graph associated to this `HLC` instance, cutting the dendrogram
        at the given `threshold`. If the threshold is `None`, the
        optimal threshold will be selected using the partition density
        method described in Ahn et al, 2010. Returns a generator that
        will generate the clusters one by one.
        """
        if threshold is None:
            return self._run_iterative()
        else:
            return self._run_single(threshold)

    def get_edge_similarity_graph(self):
        """Calculates the edge similarity graph of the graph assigned
        to this `HLC` instance."""

        # Construct the line graph
        linegraph = self.graph.linegraph()

        # Create an adjacency list representation (we already have an edgelist)
        # and select the appropriate similarity function
        if "weight" in self.graph.edge_attributes():
            similarity = TanimotoSimilarityCalculator(self.graph).get_similarity
        else:
            similarity = JaccardSimilarityCalculator(self.graph).get_similarity

        # For each edge in the line graph, compute a similarity score
        scores = []
        append, edgelist = scores.append, self._edgelist    # prelookups
        for edge in linegraph.es:
            (a, b), (c, d) = edgelist[edge.source], edgelist[edge.target]
            if a == c:
                append(similarity(b, d))
            elif a == d:
                append(similarity(b, c))
            elif b == c:
                append(similarity(a, d))
            else:   # b == d
                append(similarity(a, c))

        linegraph.es["score"] = scores
        return linegraph

    def _run_single(self, threshold):
        """Runs the hierarchical link clustering algorithm on the
        graph associated to this `HLC` instance, cutting the dendrogram
        at the given threshold. Returns a generator that will generate the
        clusters one by one.

        :Parameters:
        - threshold: the level where the dendrogram will be cut
        """
        # Record the threshold in last_threshold
        self.last_threshold = threshold
        self.last_partition_density = None

        # Construct the edge similarity graph
        linegraph = self.get_edge_similarity_graph()

        # Remove unnecessary edges
        linegraph.es(score_le=threshold).delete()

        # Process the connected components of the linegraph and build the result
        clusters = linegraph.clusters()
        result = [set() for _ in xrange(len(clusters))]
        for edge, cluster_index in izip(self._edgelist, clusters.membership):
            result[cluster_index].update(edge)
        return (list(cluster) for cluster in result
                if len(cluster) >= self.min_size)

    def _run_iterative(self):
        """Runs the hierarchical link clustering algorithm on the given graph,
        cutting the dendrogram at the place where the average weighted partition
        density is maximal. Returns a generator that will generate the clusters
        one by one.

        :Parameters:
        - graph: the graph being clustered
        - min_size: minimum size of clusters
        """

        # Construct the line graph
        linegraph = self.get_edge_similarity_graph()

        # Sort the scores
        sorted_edges = sorted(linegraph.es, key=itemgetter("score"),
                              reverse=True)

        # From now on, we only need the edge list of the original graph
        del linegraph

        # Set up initial configuration: every edge is a separate cluster
        clusters = EdgeClustering(self._edgelist)

        # Merge clusters, keep track of D, find maximal D
        max_d, best_threshold, best_membership = -1, None, None
        prev_score = None
        merge_edges = clusters.merge_edges       # prelookup
        for edge in sorted_edges:
            score = edge["score"]

            if prev_score != score:
                # Check whether the current D score is better than the best
                # so far
                if clusters.d >= max_d:
                    max_d, best_threshold = clusters.d, score
                    best_membership = list(clusters.membership)
                prev_score = score

            # Merge the clusters
            merge_edges(edge.source, edge.target)

        del clusters
        max_d *= 2 / self.graph.ecount()

        # Record the best threshold and partition density
        self.last_threshold = best_threshold
        self.last_partition_density = max_d

        # Build the result
        result = defaultdict(set)
        for edge, cluster_index in izip(self._edgelist, best_membership):
            result[cluster_index].update(edge)
        return (list(cluster) for cluster in result.itervalues()
                if len(cluster) >= self.min_size)


def hlc_single(graph, threshold = 0.66, min_size = 3):
    """Runs the hierarchical link clustering algorithm on the given graph,
    cutting the dendrogram at the given threshold. Returns a generator
    that will generate the clusters one by one.
    
    :Parameters:
    - graph: the graph being clustered
    - threshold: the level where the dendrogram will be cut
    - min_size: minimum size of clusters
    """

    # Construct the line graph
    linegraph = graph.linegraph()

    # Create an adjacency list and an edge list representation
    edgelist = graph.get_edgelist()
    adjlist = [set(graph.neighbors(i)).union([i])
               for i in xrange(graph.vcount())]

    # For each edge in the line graph, compute a similarity score
    scores = []
    for edge in linegraph.es:
        (a, b), (c, d) = edgelist[edge.source], edgelist[edge.target]
        if a == c:
            scores.append(jaccard(adjlist[b], adjlist[d]))
        elif a == d:
            scores.append(jaccard(adjlist[b], adjlist[c]))
        elif b == c:
            scores.append(jaccard(adjlist[a], adjlist[d]))
        else:   # b == d
            scores.append(jaccard(adjlist[a], adjlist[c]))

    # Assign the similarity scores, remove unnecessary edges
    linegraph.es["score"] = scores
    linegraph.es(score_le=threshold).delete()

    # Process the connected components of the linegraph and build the result
    clusters = linegraph.clusters()
    result = [set() for _ in xrange(len(clusters))]
    for edge, cluster_index in izip(edgelist, clusters.membership):
        result[cluster_index].update(edge)
    return (list(cluster) for cluster in result if len(cluster) >= min_size)


class HierarchicalLinkClusteringApp(object):
    """\
    Usage: %prog [options] input_file

    Runs a hierarchical link clustering on the given graph according
    to the method of Ahn et al.
    """

    def __init__(self):
        self.parser = OptionParser(usage=dedent(self.__doc__).strip())
        self.parser.add_option("-f", "--format", metavar="FORMAT",
                dest="format",
                help="assume that the input graph is in the given FORMAT")
        self.parser.add_option("-s", "--min-size", metavar="K",
                dest="min_size", default=3,
                help="print only clusters containing at least K nodes")
        self.parser.add_option("-t", "--threshold", metavar="THRESHOLD",
                dest="threshold", type=float,
                help="use the given THRESHOLD to cut the dendrogram. "
                     "If not specified, the threshold will be determined "
                     "automatically.")
        self.parser.add_option("-q", "--quiet", action="store_true",
                dest="quiet", help="quiet mode, print the result only")
        self.parser.add_option("-W", "--no-weights", action="store_true",
                dest="no_weights", help="ignore edge weights even if they "
                "are present in the original graph")

        self.log = logging.getLogger("hlc")

        self.options = None
        
    def run(self):
        """Runs the application."""
        self.options, args = self.parser.parse_args()

        level = logging.WARNING if self.options.quiet else logging.INFO
        logging.basicConfig(level=level, format="%(message)s")

        if not args:
            self.parser.print_help()
            sys.exit(1)

        for arg in args:
            self.process_file(arg)

    def process_file(self, filename):
        """Loads a graph from the given file, runs the clustering
        algorithm on it and prints the clusters to the standard
        output."""
        self.log.info("Processing %s..." % filename)

        graph = load(filename, format=self.options.format)

        # If the graph has weights and we want to ignore them, delete them
        if self.options.no_weights and "weight" in graph.edge_attributes():
            del graph.es["weight"]

        # If the graph is directed, we have to make it undirecteed
        if graph.is_directed():
            graph.to_undirected(combine_edges="sum")
            self.log.warning("Converted directed graph to undirected.")

        # Set up the "name" attribute properly
        if "label" in graph.vertex_attributes():
            graph.vs["name"] = graph.vs["label"]
            del graph.vs["label"]
        elif "name" not in graph.vertex_attributes():
            graph.vs["name"] = [str(i) for i in xrange(graph.vcount())]

        # Run the algorithm, get the result generator
        self.log.info("Calculating clusters, please wait...")
        algorithm = HLC(graph, self.options.min_size)
        results = algorithm.run(self.options.threshold)

        # Print the optimal threshold if we determined it automatically
        if self.options.threshold is None:
            self.log.info("Threshold = %.6f" % algorithm.last_threshold)
            self.log.info("D = %.6f" % algorithm.last_partition_density)

        # Print the results
        for community in results:
            print "\t".join(graph.vs[community]["name"])


def main():
    """Main entry point for the application when run from the command line"""
    return HierarchicalLinkClusteringApp().run()

if __name__ == "__main__":
    sys.exit(main())
