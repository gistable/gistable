#!/usr/bin/env python  

import sys
import html2text
from optparse import OptionParser
import httplib
import urllib2
import re

message = '\nPython script search totalhash.com see http://totalhash.com/help/ for examples'
parser = OptionParser(message)
parser.add_option('-r', '--report', dest='r', help='print out analysis report ./totalhash.py -r sha256', action='store')
parser.add_option('-s', '--search', dest='s', help='search totalhash ./totalhash.py -s ip:127.0.0.1 (search terms: av: dnsrr: email: filename: hash: ip: mutex: pdb: registry: url: useragent: version: )', action='store')

(options, args) = parser.parse_args()



if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)

if options.s:
    request = urllib2.Request('http://totalhash.com/search/%s' % options.s)
    opener = urllib2.build_opener()
    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE+8.0; Windows NT 5.1; Trident/4.0;)')
    data = opener.open(request).read()
    results = re.findall("\x3ch3\x3eDisplaying.*?of (.*?) results\x3c\x2fh3\x3e", data, re.DOTALL)
    total = results[0]
    if total is '0':
        print "\n[Total results - %s]" % total
    else:
	print "\n[Total results - %s]" % total
        c = '0'
        print "\nTimestamp, sha1, packer"
        while int(c) < int(total):
            request = urllib2.Request('http://totalhash.com/search/%s/%s' % (options.s, c))
            opener = urllib2.build_opener()
            request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE+8.0; Windows NT 5.1; Trident/4.0;)')
            data = opener.open(request).read()
            e = re.findall("href\x3d\x22/analysis/(.*?)\x22\x3e.*?\x3ctd.*?width\x3d15\x25\x3e(.*?)\x3c\x2ftd\x3e.*?\x3c\x2ftd\x3e.*?\x3ctd\x3e.*?\x3c\x2ftd\x3e.*?\x3ctd\x3e(.*?)\x3c\x2ftd\x3e", data, re.DOTALL)
            if e:
                c = int(c) + 20
                for m in e:
                    print "%s, %s, %s" % (m[1],m[0],m[2])
            else:
                print "[No results found]"


if options.r:
    request = urllib2.Request('http://totalhash.com/analysis/%s' % options.r)
    opener = urllib2.build_opener()
    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE+8.0; Windows NT 5.1; Trident/4.0;)')
    data = opener.open(request).read()
    d = data.decode('utf-8').strip()
    e = re.findall("\x3ctable class\x3d\x22analysis\x22\x3e(.*?)\x3c\x2fdiv\x3e\x3c\x21\x2d\x2d \x23content \x2d\x2d\x3e", d, re.DOTALL)
    if e:
        print html2text.html2text(e[0])
    else:
        print "[No results found]"
