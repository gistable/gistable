#!/usr/bin/python
# Title: Reddit Data Mining Script
# Authors: Clay McLeod
# Description: This script mines JSON data 
#  from the Reddit front page and stores it  
#  as a CSV file for analysis. 
# Section: Python
# Subsection: Data Science

want=["domain", "subreddit", "subreddit_id" "id", "author", "score", "over_18", "downs", "created_utc", "ups", "num_comments"]

# Don't touch below this point

from pprint import pprint
import requests
import json
import csv
import datetime
import time
import arff
import os
import time, sys
from sets import Set
from optparse import OptionParser
import six

parser = OptionParser()
parser.add_option("-f", "--file",
                  action="store", type="string", dest="fileName", default="results.csv",
                  help="specify the output csv file");
parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")
parser.add_option("-o", "--once",
                  action="store_true", dest="once", default=False,
                  help="run program only once")
parser.add_option("-d", "--dup",
                  action="store_false", dest="detect_duplicates", default=True,
                  help="do not detect duplicates in csv")
parser.add_option("-s", "--score",
                  action="store", type="int", dest="score_floor", default=0,
                  help="set a minimum score (ratio of upvotes to downvotes) to add to the csv")
parser.add_option("-w", "--wait",
                  action="store", type="int", dest="wait_time", default=(60 * 15),
                  help="set the amount of time to repoll the data")

(options, args) = parser.parse_args()

q = []
domains = []
subreddits = []
lastcomment=''

duplicates = 0
wait_time = options.wait_time
fileName = options.fileName

headers = {
    'User-Agent': 'Reddit Data Mining Script'
}

def log(my_string):
	if options.verbose:
		print "[+] %s" % my_string
		
	return

csvheaders = []
csvheadersset= False
authoridx = -1;
subredditidx = -1;
domainidx = -1;
utcidx = -1;
scoreidx = -1;
upsidx = -1;
downsidx = -1;
numcommentsidx = -1

if(os.path.exists(fileName)):
	with open(fileName, 'rb') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
		i = -1
		print "Detecting duplicates..."
		for row in spamreader:
			i = i + 1
			addrow = []
			
			array = row[0].split(',')
			if array[0] in want:
				csvheaders = array
				csvheadersset = True
				authoridx = array.index("author")
				subredditidx = array.index("subreddit")
				domainidx = array.index("domain")
				utcidx = array.index("created_utc")
				scoreidx = array.index("score")
				upsidx = array.index("ups")
				downsidx = array.index("downs")
				numcommentsidx = array.index("num_comments")
				continue
				
			for x in array:
				x.strip()
				addrow.append(x)
	 	
	 		if(options.detect_duplicates):
	 			for qrow in q:
	 				if (addrow[authoridx] == qrow[authoridx] and addrow[subredditidx] == qrow[subredditidx] and addrow[domainidx] == qrow[domainidx] and addrow[utcidx] == qrow[utcidx]):
	 					qrow[scoreidx] = addrow[scoreidx];
	 					qrow[upsidx] = addrow[upsidx];
	 					qrow[downsidx] = addrow[downsidx];
	 					qrow[numcommentsidx] = addrow[numcommentsidx];
	 					duplicates = duplicates + 1
	 					break
	 			else:
	 				if(options.score_floor <= int(csvheaders.index("score"))):
	 					q.append(addrow)
	 		else:
	 			if(options.score_floor <= int(csvheaders.index("score"))):
					q.append(addrow)

	log("Loaded {0} instances and updated {1} entries".format(str(len(q)),duplicates))
		

log("Outputting to %s" % fileName)

while(True):
	for i in range(1, 11):
		if(lastcomment==''):
			r = requests.get(r'http://www.reddit.com/.json?limit=100', headers=headers)
		else:
			r = requests.get(r'http://www.reddit.com/.json?limit=100&after='+lastcomment, headers=headers)
		data = r.json()
		for child in data['data']['children']:
			curr = []
			if len(csvheaders) > 0:
				csvheadersset = True
				
			for k in child['data']:
				for header in want:
					if k == header:
						curr.append(str(child['data'][k]))
						if csvheadersset == False:
							csvheaders.append(k)
					
			for qrow in q:
	 				if (curr[authoridx] == qrow[authoridx] and curr[subredditidx] == qrow[subredditidx] and curr[domainidx] == qrow[domainidx] and curr[utcidx] == qrow[utcidx]):
	 					qrow[scoreidx] = curr[scoreidx];
	 					qrow[upsidx] = curr[upsidx];
	 					qrow[downsidx] = curr[downsidx];
	 					qrow[numcommentsidx] = curr[numcommentsidx];
	 					duplicates = duplicates + 1
	 					break
											
			if(curr not in q):
				if(options.score_floor <= int(csvheaders.index("score"))):
					q.append(curr)
					
			lastcomment = child['data']['name']

	if not options.once:
		log("Sleeping {0} seconds. Data-Size: {1}".format(wait_time, str(len(q))))
	else:
		log("Finished execution. Data-Size: {0}".format(str(len(q))))
		
	if os.path.exists(fileName):
		os.remove(fileName)
	csvfile = open(fileName, 'wb')
	spamwriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
	
	spamwriter.writerow(csvheaders)
	for row in q:
		spamwriter.writerow(row)

	csvfile.close()
	if options.once:
		exit()
	time.sleep(wait_time)
	lastcomment = ''