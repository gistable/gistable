#! /usr/bin/env python

# simple script to pull data from a Zotero library RDF export
# and generate a CSV file with identifier, type of item, title,
# date, and the number of tags
# 
# Only supports book and bookSection item types, all other items are ignored
#
# The CSV file will be generated with the same base name as the
# RDF input file.

# to install dependencies:
#    pip install rdflib unicodecsv
# exmple usage:
#    python zotero-rdf-tags.py zotero-export.rdf

import argparse
import codecs
import os
import rdflib
from rdflib.namespace import DC, FOAF, RDF, DCTERMS
from unicodecsv import DictWriter


parser = argparse.ArgumentParser(description='Generate CSV from Zotero RDF')
parser.add_argument('filename', metavar='FILE',
                    help='Path to the Zoteero RDF export')

args = parser.parse_args()

ZOTERO_NS = rdflib.Namespace("http://www.zotero.org/namespaces/export#")

g = rdflib.Graph()
g.parse(args.filename)

items = []


for book, itemtype in g.subject_objects(ZOTERO_NS.itemType):
    # for now, only handle books and book sections
    if str(itemtype) not in ["book", "bookSection"]:
        continue
    tags = [str(t) for t in g.objects(book, DC.subject)]
    # use rdf about for id
    rdfid = str(book)
    # handle ids that are not full uris
    if args.filename in rdfid:
        # split on anchor marker, just keep local item did
        rdfid = rdfid.split('#', 1)[1]

    items.append({
        'identifier': rdfid,
        'type': itemtype,
        'title': g.value(book, DC.title),
        'date': g.value(book, DC.date) or '',   # not all have dates
        'tags': ', '.join(tags),
        '# tags': len(tags),
        '# tags ending in Y': len([t for t in tags if t.endswith('Y')])
        })

items = sorted(items, key=lambda k: k['# tags ending in Y'], reverse=True)

# generate csv file name based on input file
filebase, ext = os.path.splitext(os.path.basename(args.filename))
csv_filename = '%s.csv' % filebase

with open(csv_filename, 'w') as csvfile:
    # write byte-order-mark for utf-8 opening in
    csvfile.write(codecs.BOM_UTF8)
    fieldnames = ['identifier', 'type', 'title', 'date', '# tags',
                  '# tags ending in Y', 'tags']
    writer = DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for item in items:
        writer.writerow(item)

