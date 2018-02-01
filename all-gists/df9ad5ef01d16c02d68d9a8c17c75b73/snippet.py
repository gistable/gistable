
#
# twitter csv process
# write by @jiyang_viz
#
# require:
# https://github.com/edburnett/twitter-text-python
#
# download csv file from:
# https://github.com/bpb27/political_twitter_archive/tree/master/realdonaldtrump
#

import json
import csv
from ttp import ttp
from dateutil import parser as date_parser

# read csv to Dict
with open('realdonaldtrump.csv', 'r') as f:
    reader = csv.DictReader(f, delimiter = ',')
    data = list(reader)

# write to json file (same fields as csv)
with open('realdonaldtrump.json', 'w') as f:
    for item in data:
        f.write(json.dumps(item) + '\n')

# get more info from text message
parser = ttp.Parser()
for item in data:
    result = parser.parse(item['text'])
    item['tags'] = result.tags
    item['users'] = result.users
    item['reply'] = result.reply
    item['tweet_time'] = str(date_parser.parse(item['created_at']))

# write to json file (more fields)
with open('realdonaldtrump_more.json', 'w') as f:
    for item in data:
        f.write(json.dumps(item) + '\n')