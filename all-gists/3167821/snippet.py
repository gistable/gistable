import pymongo
from pymongo import Connection

conn = Connection()
db = conn['myDB']
collection = db['language']

#Creating a collection
db.language.insert({"id": "1", "name": "C", "grade":"Boring"})
db.language.insert({"id": "2", "name":"Python", "grade":"Interesting"})

#Reading it
print "After create\n",list(db.language.find())

#Updating the collection
db.language.update({"name":"C"}, {"$set":{"grade":"Make it interesting"}})
print "After update\n",list(db.language.find())

#Deleting the collection
db.language.drop()
print "After delete\n", list(db.language.find())
