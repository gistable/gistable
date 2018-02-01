#!/usr/bin/python

from time import gmtime, strftime
today=strftime("%Y%m%d")
now=strftime("%H:%M:%S")
output_file = today + '.txt'
fid = open( output_file, 'a' )

#-----------------------------------------------------------------------
# twitter-trends
#  - lists the current global trending topics
#-----------------------------------------------------------------------
from twitter import *

#-----------------------------------------------------------------------
# load our API credentials 
#-----------------------------------------------------------------------
config = {}
execfile("config.py", config)

#-----------------------------------------------------------------------
# create twitter API object
#-----------------------------------------------------------------------
twitter = Twitter(auth = OAuth(config["access_key"], config["access_secret"], config["consumer_key"], config["consumer_secret"]))

#-----------------------------------------------------------------------
# retrieve global trends.
# other localised trends can be specified by looking up WOE IDs:
#   http://developer.yahoo.com/geo/geoplanet/
# twitter API docs: https://dev.twitter.com/docs/api/1/get/trends/%3Awoeid
#-----------------------------------------------------------------------
results = twitter.trends.place(_id = 23424747)

for location in results:
	for trend in location["trends"]:
		fid.write( today + "," + now + "," + trend["name"].encode('utf-8') + "," + str(trend["tweet_volume"]) + "\n" )

fid.close()