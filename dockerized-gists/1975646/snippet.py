#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

def encode(c):
    """show the other repr of unicode str c"""
    ens=['utf-8', 'gbk', 'big5']
    print "Unicode:\t%s" % (repr(c))
    for en in ens:
        try:
            print "%s:\t%s" % (en, repr(c.encode(en)))
        except Exception, e:
            print "Error for %s: %s" % (en, str(e))

def getInput():
    c=' '.join(sys.argv[1:])
    c=unicode(c, encoding='utf-8', errors='replace')
    return c

def usage():
    print "Usage: %s <text_to_decode>" % sys.argv[0] 

def main():
    c=getInput()
    if not c:
        usage()
        exit()
    encode(getInput())
    
if __name__=='__main__':
    main()