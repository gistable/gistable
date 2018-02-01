#! /usr/bin/python2
# vim: fileencoding=utf-8 encoding=utf-8 et sw=4

import sys
import os
import xml.etree.cElementTree as ElementTree
import string
import math

def contains(poly, pos):
    cont = 0
    prev = poly[0]
    for node in poly[1:]:
        if (node[1] > pos[1]) != (prev[1] > pos[1]) and pos[0] < node[0] + \
                (prev[0] - node[0]) * (pos[1] - node[1]) / (prev[1] - node[1]):
            cont = not cont
        prev = node
    return cont

def expand(poly, dist):
    ratio = math.cos(math.radians(poly[0][0]))
    p = []
    x = poly[-2]
    y = poly[0]
    for z in poly[1:]:
        v0 = ( y[0] - x[0], (y[1] - x[1]) * ratio )
        v1 = ( z[0] - y[0], (z[1] - y[1]) * ratio )
        l0 = math.hypot(v0[0], v0[1])
        l1 = math.hypot(v1[0], v1[1])
        o = ( -v0[1] / l0 - v1[1] / l1, v0[0] / l0 + v1[0] / l1 )
        d = abs(o[0] * v1[1] - o[1] * v1[0]) / l1;
        l = math.hypot(o[0], o[1])
        # Drop it or leave it?  Drop the point
        if l > 0.2:
            p.append(( y[0] + o[0] * dist / d, y[1] + o[1] * dist / d / ratio))

        x, y = ( y, z )
    p.append(p[0])
    return p

outroot = ElementTree.Element("osm", { "version": "0.6" })
bldgroot = ElementTree.parse(sys.argv[1]).getroot()
addrroot = ElementTree.parse(sys.argv[2]).getroot()

waynodes = {}
bldgs = []
addrs = []

import rhr

# Read the building outlines
for elem in bldgroot:
    if 'id' not in elem.attrib:
        outroot.append(elem)
        continue
    id = int(elem.attrib['id'])
    if elem.tag == 'node':
        lat = float(elem.attrib['lat'])
        lon = float(elem.attrib['lon'])
        waynodes[id] = ( lat, lon )
    if elem.tag != 'way' or ('action' in elem.attrib and
            elem.attrib['action'] == 'delete'):
        outroot.append(elem)
        continue
    tags = {}
    for sub in elem:
        if sub.tag != 'tag':
            continue
        v = sub.attrib['v'].strip()
        if v:
            tags[sub.attrib['k']] = v

    if 'building' not in tags or tags['building'] == 'no':
        outroot.append(elem)
        continue

    # Tag transformations can happen here

    # Parse the geometry, store in a convenient format,
    # also find some point in the middle of the outline to be used to
    # speed up distance calculation
    way = []
    refs = []
    j = 0
    lat = 0.0
    lon = 0.0
    for sub in elem:
        if sub.tag != 'nd':
            continue
        ref = int(sub.attrib['ref'])
        if ref not in waynodes:
            continue
        way.append(waynodes[ref])
        refs.append(ref)
        j += 1
        lat += waynodes[ref][0]
        lon += waynodes[ref][1]
    lat /= j
    lon /= j
    if refs[0] != refs[-1]:
        outroot.append(elem)
        continue
    try:
        if rhr.is_rhr(way[1:]):
            nway = way
        else:
            nway = [] + way
            nway.reverse()
    except:
        outroot.append(elem)
        print('geometry error at obj ' + str(id))
        continue
    eway = expand(nway, 1.5 * 360 / 40000000)
    eeway = expand(nway, 4.0 * 360 / 40000000)
    bldgs.append(( lat, lon, way, eway, eeway, refs, tags, elem.attrib, [] ))
bldgroot = None # Make python release the XML structure


# Read the address nodes data
for elem in addrroot:
    if 'id' not in elem.attrib:
        continue
    tags = {}
    for sub in elem:
        if sub.tag != 'tag':
            continue
        v = sub.attrib['v'].strip()
        if v:
            tags[sub.attrib['k']] = v
    if elem.tag != 'node' or ('action' in elem.attrib and
            elem.attrib['action'] == 'delete'):
         continue
    lat = float(elem.attrib['lat'])
    lon = float(elem.attrib['lon'])

    id = int(elem.attrib['id'])
    if 'version' in elem.attrib:
        v = int(elem.attrib['version'])
    else:
        v = 1
    addr = ( lat, lon, tags, id, v, [] )
    addrs.append(addr)
addrroot = None

sys.stdout.write("Matching nodes to buildings\n")
for addr in addrs:
    lat, lon = addr[:2]
    # Find what if any building shapes contain this lat/lon
    for elat, elon, way, eway, eeway, refs, btags, attrs, newaddrs in bldgs:
        if 'addr:housenumber' in btags:
            continue
        if abs(elat - lat) + abs(elon - lon) > 0.005:
            continue
        if not contains(way, ( lat, lon )):
            continue
        newaddrs.append(addr)
        addr[5].append(0)
        break
sys.stdout.write("Matching nodes to buffered buildings\n")
for addr in addrs:
    if addr[5]:
        continue
    lat, lon = addr[:2]
    # Find what if any building shapes contain this lat/lon
    for elat, elon, way, eway, eeway, refs, btags, attrs, newaddrs in bldgs:
        if 'addr:housenumber' in btags:
            continue
        if abs(elat - lat) + abs(elon - lon) > 0.005:
            continue
        if not contains(eway, ( lat, lon )):
            continue
        newaddrs.append(addr)
        addr[5].append(0)
        break
sys.stdout.write("Matching nodes to double-buffered buildings\n")
for addr in addrs:
    if addr[5]:
        continue
    lat, lon = addr[:2]
    # Find what if any building shapes contain this lat/lon
    for elat, elon, way, eway, eeway, refs, btags, attrs, newaddrs in bldgs:
        if 'addr:housenumber' in btags or newaddrs:
            continue
        if abs(elat - lat) + abs(elon - lon) > 0.005:
            continue
        if not contains(eeway, ( lat, lon )):
            continue
        newaddrs.append(addr)
        addr[5].append(0)
        break

sys.stdout.write("Bulding new xml\n")
for lat, lon, way, eway, eeway, refs, tags, attrs, newaddrs in bldgs:
    # If this building contains only a single address node, copy its tags
    # to the building way and mark the node as no longer needed.
    if len(newaddrs) == 1:
        newaddrs[0][5].append(1)
        if 'source' in newaddrs[0][2]:
            newaddrs[0][2]['source:addr'] = newaddrs[0][2]['source']
            del newaddrs[0][2]['source']
        tags.update(newaddrs[0][2])
        attrs['action'] = 'modify'
        if not rhr.is_rhr(way[1:]):
            refs.reverse()

    elem = ElementTree.SubElement(outroot, "way", attrs)
    for k in tags:
        ElementTree.SubElement(elem, 'tag', { 'k': k, 'v': tags[k] })
    for ref in refs:
        ElementTree.SubElement(elem, 'nd', { 'ref': str(ref) })

# Add remaining addresses as nodes
for lat, lon, tags, id, v, bbs in addrs:
    if 1 in bbs:
        continue

    i = id
    if i < 0:
        i -= 2000000
    elem = ElementTree.SubElement(outroot, "node", {
        'lat': str(lat),
        'lon': str(lon),
        "version": str(v),
        "id": str(i) })
    for k in tags:
        ElementTree.SubElement(elem, 'tag', { 'k': k, 'v': tags[k] })

sys.stdout.write("Writing .osm's\n")
ElementTree.ElementTree(outroot).write("output.osm", "utf-8")