#! /usr/bin/env python

from configobj import ConfigObj
import sys
import StringIO
import re
from pprint import pprint

if len(sys.argv) < 3:
	print 'Usage: ducky-convert.py <keyboard.properties> <layout.properties>'
	sys.exit()

layout_file = open(sys.argv[2]).read()

#get rid of the trailing '//' since configobj doesn't like them
out = StringIO.StringIO(re.sub(r'//', '#', layout_file))
layout = ConfigObj(out)

all_keys = open(sys.argv[1]).read()
out = StringIO.StringIO(re.sub(r'//', '#', all_keys))
all_keys = ConfigObj(out)

formatted = {}


for k,v in layout.items():
	if type(v) is list:
		#print 'v is a list'
		#print 'parsing ' + k + ' = ' + str(v)
		v_list  = v[::-1]
		for key in v_list:
			if key in all_keys.keys():
				#print 'looking up ' + key
				code = all_keys[key]
			
			if 'KEY_NON_US_100' in key:
				code = 100
			
			#print key + ' = ' + code
			nindex = v_list.index(key)
			#print key + ' is at index ' + str(nindex)
			try:
				v_list[nindex] = hex(int(code))
				#print 'converted to hex'
			except TypeError and ValueError:
				v_list[nindex] = code

		if len(v_list) is 2:
			formatted["\\x" + k[-2:]] = "\\%s\\x00\\x00\\%s\\x00\\x00\\x00\\x00" % (v_list[0][1:], v_list[1][1:])
		elif len(v_list) is 3:
			formatted["\\x" + k[-2:]] = "\\%s\\x00\\x00\\%s\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\%s\\x00\\x00\\x00\\x00" % (v_list[0][1:], v_list[1][1:], v_list[2][1:])

	elif type(v) is str:
		#print 'v is a string'
		#print 'parsing ' + k + ' = ' + str(v)
		if v in all_keys.keys():
			#print 'looking up ' + str(v)
			code = str(hex(int(all_keys[v])))
		
		if 'KEY_NON_US_100' in v:
			code = str(hex(100))
		
		#print v + ' = ' + code
		formatted["\\x" + k[-2:]] = "\\x00\\x00\\x00\\%s\\x00\\x00\\x00\\x00" % code[1:]
		#print 'converted to hex'

pprint(formatted)