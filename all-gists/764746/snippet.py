import pymongo
import json
from pymongo import Connection

def connect_to_mongo(host, port, database, collection):
	connection = Connection(host, port)
	db = connection[database]
	collection = db[collection]
	return collection

collection = connect_to_mongo("localhost", 27017, "pdfs", "malware")

hash_count = {}

for md5 in collection.find( {}, {"hash_data.hashes.objects.object.md5": 1, '_id':0}):
	rjson =  json.dumps(md5)
	ruse = json.loads(rjson)
	hash_data = ruse.get("hash_data")
	hashes = hash_data.get("hashes")
	objects = hashes.get("objects")
	object = objects.get("object")
	
	for obj in object:
		md5 = str(obj.get("md5"))
		if md5 in hash_count == True:
			amount = hash_count[md5]
			hash_count = amount + 1
		else:
			hash_count[md5] = 1
	
for k, v in hash_count.iteritems():
	if v > 1:
		print k, v