#!/usr/bin/env python

import xml.etree.ElementTree as ET
import sys
import re

class OutlinerParser:
    def __init__(self):
        self.indent = 0
        self.is_note = False
        self.is_root = False

    def start(self, tag, attr):
        if re.match('^{.+}item$', tag):
            self.indent += 1
        if re.match('^{.+}note$', tag):
            self.is_note = True
        if re.match('^{.+}root$', tag):
            self.is_root = True

    def end(self, tag):
        if re.match('^{.+}item$', tag):
            self.indent -= 1
        if re.match('^{.+}note$', tag):
            self.is_note = False
        if re.match('^{.+}root$', tag):
            self.is_root = False

    def data(self, data):
        if not self.is_root:
            return

        print '\t' * self.indent,
        if self.is_note:
            print '| ',
        print data.encode('utf-8')

    def close(self):
        pass

def main():
    parser = ET.XMLTreeBuilder(target=OutlinerParser())
    parser.feed(sys.stdin.read())
    parser.close()

if __name__ == '__main__':
    main()
