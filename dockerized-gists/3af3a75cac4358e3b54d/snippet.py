"""
Generates a simple dot graph class hierarchy from a set of base classes.

Usage::

    $ python pyhierarchy2dot.py sqlalchemy.String sqlalchemy.Integer sqlalchemy.DateTime
"""

import sys
import importlib

import pydot as dot

class ClassDescription(object):
    _cls_cache = {}

    def __init__(self, cls):
        self.cls = cls
        self.cls_name = cls.__name__
        self.graph_node = dot.Node(self.cls_name)
        self.parents = map(self.from_cls, self.cls.__bases__)

    @classmethod
    def from_name(cls, name):
        mod_name, _, cls_name = name.rpartition(".")
        mod = importlib.import_module(mod_name)
        return cls.from_cls(getattr(mod, cls_name))

    @classmethod
    def from_cls(cls, c):
        if c not in cls._cls_cache:
            cls._cls_cache[c] = cls(c)
        return cls._cls_cache[c]


def add_parent_edges(graph, cd):
    graph.add_node(cd.graph_node)
    for parent in cd.parents:
        graph.add_edge(dot.Edge(cd.graph_node, parent.graph_node))
        add_parent_edges(graph, parent)


def main(argv):
    graph = dot.Dot(graph_type="digraph")
    for arg in argv[1:]:
        cd = ClassDescription.from_name(arg)
        add_parent_edges(graph, cd)
    graph.write_png("/tmp/pyhierarchy2dot.png")
    print "Graph saved to /tmp/pyhierarchy2dot.png"
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
