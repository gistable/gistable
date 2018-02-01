import pymongo
import sys
import time
from bson import json_util

# IMPORTANT: this is undocumented and is a work-in-progress. Please do
# not use in Production!!!
# 
# This script extracts glucose data from mongodb in JSON format. Can be
# used on an OpenAPS rig, in combination with xDrip Android app, to 
# loop when offline. Edison/Pi needs to be connected to Android device
# via personal WiFi hotspot or bluetooth tethering
#
# 1 - Install mongodb on OpenAPS rig (tested on Edison, untested on Pi)
# 2 - Configure xDrip Android app to upload to mongodb
# 3 - Copy this script onto OpenAPS rig
# 4 - Create OpenAPS device e.g. 'mongo' which executes this script
# 5 - Create OpenAPS report which uses new device to obtain JSON output
# 6 - Use this report as part of your loop

# Maximum number of records to be included in report (default = last 24 hours)
max_report_size=288

# Number of glucose records required can optionally be overriden by command-line arg
if(len(sys.argv) > 1):
    max_report_size = int(sys.argv[1])

# Connect to local mongo instance
try:
  conn=pymongo.MongoClient('localhost', 27017)    
except pymongo.errors.ConnectionFailure, e:
  print "Could not connect to MongoDB: %s" % e
  sys.exit(1)

# Use the xdrip database
db = conn.xdrip

# Delete all non-sgv records (e.g. calibrations)
db.entries.delete_many({"type": {"$ne":"sgv"}})

# Delete all remaining records which are more than 48 hours old
epoch_now = int(time.time()) * 1000
epoch_cutoff = epoch_now - (48*60*60*1000)
db.entries.delete_many({"date": {"$lt": epoch_cutoff}})

# Start outputting records in JSON format
print "["
records = db.entries.find().sort([("date", pymongo.DESCENDING)])
num_of_results= records.count()
loop_index = 0 
for rec in records:
  loop_index = loop_index + 1
  print json_util.dumps(rec, sort_keys=True, indent=2, default=json_util.default)
  if ((loop_index < num_of_results) and (loop_index < max_report_size)):
    print ","
  else:
    break
print "]"

# End