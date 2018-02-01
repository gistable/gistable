# -*- coding: utf-8 -*-

# This script requires pygerduty: https://github.com/dropbox/pygerduty

# Given a start date and end date, this sample will export the description and
# notes from all incidents to a CSV file. The CSV file is formatted for use
# with Excel.
# This will export to incident_notes_[start date]_-_[end date].csv in the same
# directory that this script is located in.
# This would be most useful to join with a CSV file as exported from PagerDuty.

# Usage: edit subdomain and specify an API key (must have full access) below.
# (What's the subdomain? Example: http://demo.pagerduty.com --> "demo")
# Then run: python incidents.py [start date: YYYY-MM-DD] [end date: YYYY-MM-DD]
# Example: python incidents.py 2015-01-01 2015-03-31

import pygerduty
pager = pygerduty.PagerDuty("[subdomain]", "[api key]")

import sys
import os.path

startdate, enddate = sys.argv[1:]

# This function escapes quotes in notes in a way that's Excel compatible.
# All other characters, including comma and new-line, are handled correctly
# by way of being included within the surrounding quotes.

def escape( str ):
	str = str.replace("\"", "\"\"")
	return str

my_filename = sys.path[0] + "/incident_notes_%s_-_%s.csv" % (startdate, enddate)
with open(my_filename, 'w',1) as the_file:
	the_file.write("Incident ID,Description,Notes\n")
	for incident in pager.incidents.list(since=startdate, until=enddate):
		if hasattr(incident.trigger_summary_data, 'subject'):
			my_description = incident.trigger_summary_data.subject
		elif hasattr(incident.trigger_summary_data, 'description'):
			my_description = incident.trigger_summary_data.description
		my_line = '%s,"%s","' % (incident.incident_number, escape(my_description))
		my_count = 0
		for note in incident.notes.list(incident_id=incident.incident_number):
			my_count += 1
			if my_count > 1:
				my_line += "\n"
			my_line += "%s, %s: %s" % (escape(note.user.name), escape(note.created_at), escape(note.content))
		my_line += "\"\n"
		the_file.write(my_line)