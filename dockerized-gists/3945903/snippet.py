#! /usr/bin/env python

from xml.etree import ElementTree

from xml.sax.handler import ContentHandler
from xml.sax import parse

import csv


class Converter(ContentHandler):

    def __init__(self, csv_filename):
        self.output_file = open(csv_filename, 'w')
        self.csv_writer = csv.DictWriter(self.output_file, ['lb','s', 'ec', 'hn', 'in', 'dt', 'by', 'na', 'ts', 'ng', 'tn', 'lt', 't', 'rc', 'sc', 'rm'])

    def __del__(self):
        self.output_file.close()

    def startDocument(self):
        self.csv_writer.writeheader()

    def startElement(self, name, attrs):
        if name == 'httpSample':
            adict = {}
            for name in attrs.getNames():
                adict[name] = attrs.getValue(name)
            self.csv_writer.writerow(adict)


def main(filename):
    parse(filename, Converter("%s.csv" % (filename)))


if __name__ == '__main__':
    import sys

    #try:
    main(sys.argv[1])
    #except:
    #    print("\nUsage: %s input_file" % (sys.argv[0]))
    #    print("\n  Input file should contain http samples created by JMeter in JTL format.\n")
