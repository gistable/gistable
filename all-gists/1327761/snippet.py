#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (c) 2011 Raphael Jasjukaitis <webmaster@raphaa.de>

import csv
import os
import sys

from optparse import OptionParser
from time import time

class Converter():
    """Converts an CSV instapaper export to a Chrome bookmark file."""

    def __init__(self, file):
        self._file = file

    def parse_urls(self):
        """Parses the file and returns a folder ordered list."""
        efile = open(self._file)
        urls = csv.reader(efile, dialect='excel')
        parsed_urls = {}
        urls.next()
        for url in urls:
            folder = url[3].strip()
            if folder not in parsed_urls.keys():
                parsed_urls[folder] = []
            parsed_urls[folder].append([url[0], url[1]])
        return parsed_urls

    def convert(self):
        """Converts the file."""
        urls = self.parse_urls()
        t = int(time())
        content = ('<!DOCTYPE NETSCAPE-Bookmark-file-1>\n'
                   '<META HTTP-EQUIV="Content-Type" CONTENT="text/html;'
                   ' charset=UTF-8">\n<TITLE>Bookmarks</TITLE>'
                   '\n<H1>Bookmarks</H1>\n<DL><P>\n<DT><H3 ADD_DATE="%(t)d"'
                   ' LAST_MODIFIED="%(t)d">Instapaper</H3>'
                   '\n<DL><P>\n' % {'t': t})
        for folder in urls.keys():
            content += ('<DT><H3 ADD_DATE="%(t)d" LAST_MODIFIED="%(t)d">%(n)s'
                        '</H3>\n<DL><P>\n' % {'t': t, 'n': folder})
            for url in urls[folder]:
                content += ('<DT><A HREF="%s" ADD_DATE="%d">%s</A>\n'
                            % (url[0], t, url[1]))
            content += '</DL><P>\n'
        content += '</DL><P>\n' * 3
        ifile = open('chrome-bookmarks.html', 'w')
        ifile.write(content)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'File as argument is required.'
        sys.exit(1)
    file = sys.argv[1]
    if not os.path.isfile(file):
        print 'The file does not exist!'
        sys.exit(1)
    converter = Converter(file)
    converter.convert()
    sys.exit(0)