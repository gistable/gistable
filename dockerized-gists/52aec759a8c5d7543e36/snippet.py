#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
from lxml import etree
import StringIO
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

file = open('1password.csv','w')

parser = etree.XMLParser(encoding='utf-8', recover=True)

tree = etree.parse('keepassx.xml', parser)

groups = tree.xpath('/database/group')

# for group in range(len(groups)):
# 	subgroup = groups[group].xpath('group')

# 	if (len(subgroup)):
# 		# print len(subgroup)
# 		for node in subgroup:
# 			print len(subgroup), groups[group].getchildren()[0].text, node[0].text
# 	else:
# 		print len(subgroup), groups[group].getchildren()[0].text, len(groups[group].xpath('entry'))

def getnodes(gr, num):
	subgroup	= gr.xpath('group')
	entry		= gr.xpath('entry')
	groupTitle 	= gr[0].text

	if (len(entry)):
		for item in entry:
			title 		= str(item[0].text)
			username 	= str(item[1].text)
			password 	= str(item[2].text)
			url 		= str(item[3].text)
			comment 	= str(item[4].text)

			# print 'Title:', item[0].text.encode("UTF-8")
			s = ('"'+title+'","'+url+'","'+username+'","'+password+'","'+comment+'"').replace('None','')
			file.write(s+'\n')

	if(len(subgroup)):
		for node in range(len(subgroup)):
			# print 'getnodes'
			getnodes(subgroup[node], node)

for group in range(len(groups)):
	getnodes(groups[group], group)

file.close()
