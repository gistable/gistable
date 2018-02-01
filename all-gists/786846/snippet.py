#!/usr/bin/python

__description__ = 'Get the MDL list and search a blob'
__author__ = 'Brandon Dixon'
__version__ = '1.0'
__date__ = '2011/19/01'

import optparse
import os

global mdl
mdl = "http://www.malwaredomainlist.com/mdlcsv.php"

def get_list():
	print "== Downloading MDL =="
	os.system('rm /tmp/*')
	os.system('wget -t 1 -P /tmp ' + mdl)
	print "== Downloaded List =="

def parse_list(filename):
	print "== Parsing File =="
	ips = []
	fd = file(filename,'r')
	lines = fd.readlines()
	for line in lines:
		if(line.strip()):
			data = line.split(',')
			ips.append(data[2].strip().replace('\"',''))
	fd.close()
	ips = f7(ips)
	return ips
	print "== File Parsed =="

def check_blob(filename, ips):
	print "== Checking Blob =="
	fd = file(filename, 'r')
	lines = fd.readlines()
	check = []
	for line in lines:
		for ip in ips:	
			if(len(ip) > 4):
				result = line.find(str(ip.strip()))
				if(result >= 0):
					check.append(line.strip())

	check = f7(check)
	return check

def f7(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]

def write_list(filename, parsed):
	print "== Writing List =="
	fd = file(filename, 'w')
	for url in parsed:
		fd.write(url + '\n')
	fd.close()
	print "== List Written =="

def main():
    oParser = optparse.OptionParser(usage='usage: %prog [options]\n' + __description__, version='%prog ' + __version__)
    oParser.add_option('-f', '--file', default='', type='string', help='blob file')
    (options, args) = oParser.parse_args()

    if options.file:
	get_list()
	parsed = parse_list('/tmp/mdlcsv.php')
	check = check_blob(options.file, parsed)
	print "== Results =="
	for item in check:
		print item
	
    else:
        oParser.print_help()
        return

if __name__ == '__main__':
    main()
