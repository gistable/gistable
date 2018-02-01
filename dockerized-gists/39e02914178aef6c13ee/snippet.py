#!/usr/bin/python

# Yahoo Contact Exporter - used to retrieve a csv file from address.yahoo.com, including Facebook contacts
# Copyright (C) 2012  Jonathan Earl Camp

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import sys
import string
import csv
from bs4 import BeautifulSoup
from nameparser import HumanName

#read input file argument or print usage help
if(len(sys.argv) > 1):
	inputfilename = sys.argv[1]
	try:
		f1 = open(inputfilename)
	except IOError as e:
		print "Error reading input file: I/O error({0}): {1}".format(e.errno, e.strerror)
		sys.exit(1)
else:
	print "Command-line usage: yahoocontactexport inputfile.html [outputfile.csv]"
	print "Output file defaults to yahoocontacts.csv if not specified"
	print "You can drag the input html file onto the executable in Windows"
	sys.exit(1)

#if an output file is specified, try to open it. otherwise, write to yahoocontacts.csv
if(len(sys.argv) == 3):
	outputfilename = sys.argv[2]
	try:
		f2 = open(outputfilename, 'wb')
	except IOError as e:
		print "Error writing to output file: I/O error({0}): {1}".format(e.errno, e.strerror)
		sys.exit(1)
else:
	try:
		f2 = open('yahoocontacts.csv','wb')
	except IOError as e:
		print "Error writing to output file: I/O error({0}): {1}".format(e.errno, e.strerror)
		sys.exit(1)

#csv writer helper. modify header if you need a custom csv format
csvwriter = csv.writer(f2)
csvwriter.writerow(['Name','Email Address'])

#do work, son
soup = BeautifulSoup(f1)

#modify find queries as needed
for contact in soup.find_all("div", { "class" : "tcell" }):
    try:
        nameNode = contact.div
        if not nameNode:
            continue
        name = HumanName(nameNode.span.b.text.strip())
        emailNode = contact.find("div", {"class" : "c"})
        if (emailNode):
            csvwriter.writerow([unicode(name).encode('utf-8'),emailNode.text.encode('utf-8')])
    except:
	print "error with: "
	print contact
f1.close()
f2.close()
