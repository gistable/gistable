#!/usr/bin/python
# -*- coding: utf8 -*-

# We'll use the pyzotero project for server access
# See packages.python.org/Pyzotero/
from pyzotero import zotero

import sys

# Python's built-in CSV support is pretty nice
# See http://docs.python.org/library/csv.html
import csv

if __name__ == "__main__":
	
	# Connect to Zotero server
	# You'll need to replace the first number with your user ID number
	# and the XXXXX with an API key with write access to your library.
	server = zotero.Zotero('5770', 'XXXXX')

	# Connect to datafile
	# Set the source CSV datafile here
	csvfile = open("/home/ajlyon/Desktop/in.csv", "rb")
	# Python can try to guess the delimiters and such. Cool!
	dialect = csv.Sniffer().sniff(csvfile.read(1024))
	csvfile.seek(0)
	# We could have used a csv.DictReader to get a Python dict
	# from the input, but I didn't use one here.
	reader = csv.reader(csvfile, dialect)

	items = []
	sitems = []
	
	for item in reader:
		# My input has the type in the seventh column (0-based indexing)
		# I need to set the corresponding Zotero type
		# For types and the fields they support, see Frank Bennett's guide
		# to types and fields: http://gsl-nagoya-u.net/http/pub/csl-fields
		if item[6] == "письмо":
			itemtype = "letter"
		elif item[6] == "рукопись":
			itemtype = "manuscript"
		elif item[6] == "статья":
			itemtype = "journalArticle"
		elif item[6] == "биографический документ":
			itemype = "manuscript"
		elif item[6] == "документы общественной деятельности":
			itemtype = "manuscript"
		else:
			# This is mainly because I have a header line I want to omit
			# We could set a fallback type instead, or I could have parsed
			# out the header using csv.DictReader
			print "Skipping %s with type %s" % (item[0], item[6])
			continue
		print "%s is a %s" % (item[0], itemtype)
		# pyzotero grabs the template dict from the server
		zitem = server.item_template(itemtype)
		# And we start setting the item fields
		zitem['archive'] = "НА РТ"
		# We can do basic manipulation
		zitem['archiveLocation'] = "ф. Р-2461, оп. 1 д. %s" % (item[0])
		zitem['title'] = item[1]
		zitem['date'] = item[2]
		zitem['language'] = item[5]

		# This is a thorny bit-- if you set any illegal fields, the request
		# will fail. So make sure you use fields that exist on the types you
		# are sending!
		if item[3]:
			if itemtype == "manuscript":
				zitem['numPages'] = "%s л." % (item[3])
			elif itemtype == "journalArticle":
				zitem['extra'] = "%s л." % (item[3])
			elif itemtype == "letter":
				zitem['extra'] = "%s л." % (item[3])
		if itemtype == "manuscript":
			zitem['manuscriptType'] = item[6]
		# Do nothing for letters and articles

		print "Item %s prepared" % (zitem['title'])
		items.append(zitem)

	# Before saving, check that the item keys are legal
	# This will throw KeyError if the keys are bad
	try:
		server.check_items
	except AttributeError:
		# The check_items method appeared in 1187a40efe71ce42117c
		print "Not checking for bad keys. Upgrade to the latest pyzotero!"
	else:
		server.check_items(items)

	# The server API takes only 50 items at a time 
	while items:
		result = server.create_items(items[:50])
		del items[:50]
		# We also want to put them in a specific collection
		# The easy way to find a collection ID is to view the
		# collection online and get it from the URL
		if server.addto_collection("HZ7RRUBC",result):
			print 'Items added to collection'
		for res in result:
			# We print some output for good measure
			# This output includes the item key, which could be used to
			# fetch the items again for more processing
			print 'Loc.: %s | Title: %s (%s)' % (res['archiveLocation'], res['title'], res['key'])
			sitems.append(result)
	# If you want to delete the items, or do anything else with them, you could do that here
	"""
	for sitem in sitems:
		server.delete_item(sitem)
	"""
