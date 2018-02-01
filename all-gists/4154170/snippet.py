#!/usr/bin/env python
# -*- coding: utf-8 -*-
# The code is dirty.

from __future__ import print_function, unicode_literals
import xml.sax

class OSMHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.osm_nodes = {}
        self._way = None
        self._first = True

    def startElement(self, name, attrs):
        if name == "node":
            self.osm_nodes[attrs["id"]] = (attrs["lat"], attrs["lon"])
        elif name == "way":
            self._way = {"id": attrs["id"], "nodes": [], "tags": {}}
        if self._way is not None:
            if name == "nd":
                self._way["nodes"].append(attrs["ref"])
            elif name == "tag":
                self._way["tags"][attrs["k"]] = attrs["v"]

    def endElement(self, name):
        if name == "way":
            if self._way is not None:
                if self._way["tags"].get("building", None) is not None:
                    nodes_json = ", ".join("[{0[0]}, {0[1]}]".format(self.osm_nodes[node_id]) for node_id in self._way["nodes"])
                    addr = "null"
                    if self._way["tags"].get("addr:street", None) is not None and self._way["tags"].get("addr:housenumber", None) is not None and self._way["tags"].get("addr:city", None) in ("Великий Новгород", None):
                        addr = "\"{0}, {1}\"".format(self._way["tags"]["addr:street"], self._way["tags"]["addr:housenumber"])
                    if True or addr != "null":
                        if not self._first:
                            print(",\n", end="")
                        print("""  "{0:d}": {{"addr": {1}, "nodes": [{2}]}}""".format(int(self._way["id"]), addr, nodes_json).encode("utf-8"), end="")
                        self._first = False
            self._way = None

osm = OSMHandler()

parser = xml.sax.make_parser()
parser.setContentHandler(osm)
print("{")
parser.parse(open("RU-NGR.osm", "r"))
print("\n}", end="")
