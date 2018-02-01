from pymongo import MongoClient
from bson.code import Code

client = MongoClient()
db = client["dbname"]

col = db["collName"]

map = Code("function(){ if(this.fieldName){emit(this.fieldName,1);}}")
reduce = Code("function(key,values) {"
	"return Array.sum(values);"
"}")

res = col.map_reduce(map,reduce,"my_results");


response = []
for doc in res.find():
	if(doc['value'] > 1):
		count = int(doc['value']) - 1
		docs = col.find({"fieldName":doc['_id']},{'_id':1}).limit(count)
		for i in docs:
			response.append(i['_id'])



col.remove({"_id": {"$in": response}})