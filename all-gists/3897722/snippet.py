#!/usr/bin/env python
import csv
import sys

# read sample tuleap csv header to avoid some field changes
tuleapcsvfile = open('tuleap.csv', 'rb')
reader = csv.DictReader(tuleapcsvfile)


# open stdout for output
w = csv.DictWriter(sys.stdout, fieldnames=reader.fieldnames,lineterminator="\n")
w.writeheader()

defaultrow={'submitted_by': 'rdccaiy', 'submitted_on': "10/12/2012 03:11:51",'last_update_date':'10/12/2012 03:11:51'}

# read redmine csv files for convertng
with open('redmine.csv', 'rb') as redminecsvfile:
	redminereader = csv.DictReader(redminecsvfile)
	for row in redminereader:
		# reset the newrow for writing
		newrow = defaultrow
		#print row
		# mapping for multi values
		if row['Status']=='New':
			newrow['status'] = "Not Started"
		# some simple one to one mapping
		newrow['i_want_to' ]= row['Description']
		newrow['so_that'] = row['Subject']
		w.writerow(newrow)