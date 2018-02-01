#!/usr/bin/env python
# parse_toc.py

from pdfminer.pdfparser import PDFParser, PDFDocument

def parse(filename, maxlevel):
    fp = open(filename, 'rb')
    parser = PDFParser(fp)
    doc = PDFDocument()
    parser.set_document(doc)
    doc.set_parser(parser)

    outlines = doc.get_outlines()
    for (level, title, dest, a, se) in outlines:
        if level <= maxlevel:
            print ' ' * level, title


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print 'Usage: %s xxx.pdf level' % sys.argv[0]
        sys.exit(2)

    parse(sys.argv[1], int(sys.argv[2]))
