'''
Tested with:
Mongo 3.0.12
pymongo 3.3.0

Elasticsearch 2.1.2
Kibana 4.3.3
elasticsearch python 2.1.0
'''

DATABASE = 'imo' #This will be the index you need to select in Kibana, it is also the database to use in mongo to pull data from


from pymongo import MongoClient
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, parallel_bulk
from collections import deque
from tqdm import tqdm
import time
client = Elasticsearch()
mgclient = MongoClient()
db = mgclient[DATABASE]
col = db['sslog']

# Pull from mongo and dump into ES using bulk API
actions = []
for data in tqdm(col.find(), total=col.count()):
    data.pop('_id')
    action = {
        "_index": DATABASE,
        "_type": "sslog",
        "_source": data
    }
    actions.append(action)
    
    # Dump x number of objects at a time
    if len(actions) >= 100:
        deque(parallel_bulk(client, actions), maxlen=0)
        actions = []
    time.sleep(.01)