#!/opt/local/bin/python2.7
# encoding: utf-8
"""
couchimport.py
Created by Marian Steinbach on 2011-11-10.
"""

import sys
import os
import datetime
import re
from couchdbkit import *

class Measure(Document):
	station_id = StringProperty()
	datetime = ListProperty()
	sa = IntegerProperty()
	ra = IntegerProperty()

def main():
	server = Server()
	db = server.get_or_create_db("jpradiation")
	Measure.set_db(db)
	linecount = 0
	matcher = re.compile(r'"([0-9]{10})";"([0-9]{4})-([0-9]{2})-([0-9]{2}) ([0-9]{2}):([0-9]{2}):([0-9]{2})";"([^\"]+)";"([^\"]+)"')
	measures = []
	for line in sys.stdin:
		matches = matcher.match(line)
		m = Measure(
			station_id = matches.group(1),
			datetime = [int(matches.group(2)), int(matches.group(3)), int(matches.group(4)), int(matches.group(5)), int(matches.group(6)), int(matches.group(7))],
			sa = int(matches.group(8)),
			ra = int(matches.group(9))
		)
		measures.append(m)
		linecount += 1
		if linecount % 1000 == 0:
			db.bulk_save(measures)
			measures = []
	db.bulk_save(measures)
	print linecount, "rows written"


if __name__ == '__main__':
	main()
