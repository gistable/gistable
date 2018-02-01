#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Simple script to create geojson from osm files.
Prints geojson features line by line.
Currently we don't support relations.
Requires (unmodified) imposm and imposm.parser
Inspired by https://github.com/emka/OSMCouch
'''

from multiprocessing import JoinableQueue
from imposm.parser import OSMParser
from imposm.reader import CacheWriterProcess
from imposm.cache import OSMCache

import sys
import io
import json


def generateCache(filename = 'berlin.osm.pbf'):
    cache = OSMCache('.')
    coords_queue = JoinableQueue(512)
    coords_writer = CacheWriterProcess(coords_queue, cache.coords_cache, None, marshaled_data=True)
    coords_writer.start()

    parser = OSMParser(coords_callback=coords_queue.put)

    parser.parse(filename)

    coords_queue.put(None)
    coords_writer.join()
    return cache

class Handler(object):

    def __init__(self, cache, output):
        self.coordsCache = cache.coords_cache(mode='r')
        self.outputFile = io.open(output, mode='w')

    def nodeToGEOJson(self, node):
        id, tags, (lon, lat) = node
        return unicode(json.dumps({ 'id': id, 'type': 'Feature', 'geometry': { 'type': 'Point', 'coordinates': [lon, lat] } , 'properties': tags }, ensure_ascii=False) + '\n')

    def wayToGEOJson(self, way):
        id, tags, nodes = way
        coords = self.coordsCache.get_coords(nodes)
        return unicode(json.dumps({ 'id': id, 'type': 'Feature', 'geometry': { 'type': 'LineString', 'coordinates': coords }, 'properties': tags }, ensure_ascii=False) + '\n')

    def nodes_callback(self, nodes):
        for node in nodes:
            self.outputFile.write(self.nodeToGEOJson(node))
            #self.file.write(self.nodeToGEOJson(node))

    def ways_callback(self, ways):
        for way in ways:
            self.outputFile.write(self.wayToGEOJson(way))


def main(filename, output):
    #cache = generateCache(filename)
    cache = OSMCache('.')
    coords_queue = JoinableQueue(512)
    coords_writer = CacheWriterProcess(coords_queue, cache.coords_cache, None, marshaled_data=True)
    coords_writer.start()

    handler = Handler(cache, output)
    parser = OSMParser(coords_callback=coords_queue.put,
            nodes_callback=handler.nodes_callback,
            ways_callback=handler.ways_callback
            )
    parser.parse(filename)

    coords_queue.put(None)
    coords_writer.join()


if __name__ == '__main__':
    filename = sys.argv[1]
    if len(sys.argv) is 3:
        output = sys.argv[2]
    else:
        output = '/dev/stdout'
    main(filename, output)