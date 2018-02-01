##########################################################################
# THE MICRO MONGODB+PYTHON BOOK 
#
# A simple adaptation to Python + summary of 
# The Little MongoDB Book: https://github.com/karlseguin/the-little-mongodb-book
#
# javier arias losada
# twitter: @javier_arilos

# Usage suggestion: run line by line bu using pydemo project (https://github.com/pablito56/pydemo) 
# You will need a MongoDB instance up and running.
# >> pip install pymongo
# >> pip install git+https://github.com/pablito56/pydemo.git
# >> pydemo micro-pymongo.py

# ******** Chapter 1 - The Basics: 
# * 
# * https://github.com/karlseguin/the-little-mongodb-book/blob/master/en/mongodb.markdown#chapter-1---the-basics
#
# MongoDB (from "humongous") is an open-source document database, (...) MongoDB features:
# Document-Oriented: JSON-style, with dynamic schemas.
# Full Index Support: Index on any attribute.
# Replication & High Availability: Across LANs and WANs.
# Auto-Sharding: Scale horizontally.
# Querying: Rich, document-based queries.
# Fast In-Place Updates: Atomic modifiers.
# Map/Reduce: Flexible aggregation and data processing.
# GridFS: Store files of any size.
# MongoDB Management: Monitoring and backup.

# databases >> collections >> documents >> fields

# Pymongo + MongoDB make it very easy to work:
# create a client
import pymongo
from datetime import datetime
client = pymongo.MongoClient()

# use micro database
db = client['micro-mongodb-python-book']

# insert a document (a Python dict) into unicors collection
db.unicorns.insert({'name': 'Aurora', 'gender': 'f', 'weight': 450})

# both database and collection are, lazy initialized if do not exist

# mongodb is schemaless, we can insert a document with different structure
db.unicorns.insert({'client_id': 'Mickey', 'specie': 'mouse', 'weight': 0.450})

# find returns a Cursor object, we can iterate over it.
for doc in db.unicorns.find():
    print doc

# Querying data and selectors: 
# remove documents in the collection
db.unicorns.remove()

# First, insert some unicorns' data for later querying
db.unicorns.insert({'name': 'Horny',
    'dob': datetime(1992,2,13,7,47),
    'loves': ['carrot','papaya'],
    'weight': 600,
    'gender': 'm',
    'vampires': 63});
db.unicorns.insert({'name': 'Aurora',
    'dob': datetime(1991, 10, 24, 13, 0),
    'loves': ['carrot', 'grape'],
    'weight': 450,
    'gender': 'f',
    'vampires': 43});
db.unicorns.insert({'name': 'Unicrom',
    'dob': datetime(1973, 1, 9, 22, 10),
    'loves': ['energon', 'redbull'],
    'weight': 984,
    'gender': 'm',
    'vampires': 182});
db.unicorns.insert({'name': 'Roooooodles',
    'dob': datetime(1979, 7, 18, 18, 44),
    'loves': ['apple'],
    'weight': 575,
    'gender': 'm',
    'vampires': 99});
db.unicorns.insert({'name': 'Solnara',
    'dob': datetime(1985, 6, 4, 2, 1),
    'loves':['apple', 'carrot',
        'chocolate'],
    'weight':550,
    'gender':'f',
    'vampires':80});
db.unicorns.insert({'name':'Ayna',
    'dob': datetime(1998, 2, 7, 8, 30),
    'loves': ['strawberry', 'lemon'],
    'weight': 733,
    'gender': 'f',
    'vampires': 40});
db.unicorns.insert({'name':'Kenny',
    'dob': datetime(1997, 6, 1, 10, 42),
    'loves': ['grape', 'lemon'],
    'weight': 690,
    'gender': 'm',
    'vampires': 39});
db.unicorns.insert({'name': 'Raleigh',
    'dob': datetime(2005, 4, 3, 0, 57),
    'loves': ['apple', 'sugar'],
    'weight': 421,
    'gender': 'm',
    'vampires': 2});
db.unicorns.insert({'name': 'Leia',
    'dob': datetime(2001, 9, 8, 14, 53),
    'loves': ['apple', 'watermelon'],
    'weight': 601,
    'gender': 'f',
    'vampires': 33});
db.unicorns.insert({'name': 'Pilot',
    'dob': datetime(1997, 2, 1, 5, 3),
    'loves': ['apple', 'watermelon'],
    'weight': 650,
    'gender': 'm',
    'vampires': 54});
db.unicorns.insert({'name': 'Nimue',
    'dob': datetime(1999, 11, 20, 16, 15),
    'loves': ['grape', 'carrot'],
    'weight': 540,
    'gender': 'f'});
db.unicorns.insert({'name': 'Dunx',
    'dob': datetime(1976, 6, 18, 18, 18),
    'loves': ['grape', 'watermelon'],
    'weight': 704,
    'gender': 'm',
    'vampires': 165});
# Inserted some unicorns' data for later querying

# MongoDB selectors are the equivalent to WHERE clauses in relational DB's
# a selector is an object instructing how to match objects in the collection

# find all male unicorns
for doc in db.unicorns.find({'gender': 'm'}):
	print doc

# find all male unicorns that weigh more than 700 pounds
for doc in db.unicorns.find({'gender': 'm', 'weight': {'$gt': 700}}):
	print doc
	

# female unicorns which either love apples or oranges or weigh less than 500 pounds
cursor = db.unicorns.find({'gender': 'f', '$or': [{'loves': 'apple'}, {'loves': 'orange'}, {'weight': {'$lt': 500}}]})
for doc in cursor:
	print doc

# ******** Chapter 2 - Update:
# *
# * https://github.com/karlseguin/the-little-mongodb-book/blob/master/en/mongodb.markdown#chapter-2---updating
#

# We have now many unicorn documents, let's update one of them:
db.unicorns.find_one({'name': 'Roooooodles'})

# Update takes a minimum of two arguments, one Selector object to match and an update object
db.unicorns.update({'name': 'Roooooodles'}, {'weight': 590})

# Let's check the result
db.unicorns.find_one({'name': 'Roooooodles'})
# No results? How that can be? Check the result of the following

db.unicorns.find_one({'weight': 590})
# Update, by default will replace the matched document with the new document provided

# How can we update just some fields and keep the rest unchanged? $set operator
# Let's recover our wrongly updated unicorn:
db.unicorns.update({'weight': 590}, {'$set': {
    'name': 'Roooooodles',
    'dob': datetime(1979, 7, 18, 18, 44),
    'loves': ['apple'],
    'gender': 'm',
    'vampires': 99}})

db.unicorns.find_one({'name': 'Roooooodles'})
# In all previous update operations, the Roooooodles' document _id is the same

# Other update modifiers: 
# $inc for incrementing/decrementing a numeric field
db.unicorns.update({'name': 'Roooooodles'}, {'$inc': {'vampires': -2}})
db.unicorns.find_one({'name': 'Roooooodles'})

# $push for adding element to an array field
db.unicorns.update({'name': 'Roooooodles'}, {'$push': {'loves': 'carrot'}})

# update modifiers can be combined to do many operations on a single operation
db.unicorns.update({'name': 'Roooooodles'}, {'$push': {'loves': 'potato'}, '$inc': {'vampires': 6}})
db.unicorns.find_one({'name': 'Roooooodles'})

# many push and inc can on multiple elements be done in a single operation
db.unicorns.update({'name': 'Roooooodles'}, {'$push': {'loves': {'$each': ['apple', 'durian']}}, '$inc': {'vampires': 6, 'eggs': 1}})
db.unicorns.find_one({'name': 'Roooooodles'})

# mongodb supports Upserts (Update or Insert)
# Let's count hits on our application pages
db.hits.update({'page': 'unicorns'}, {'$inc': {'hits': 1}})
db.hits.find_one()

db.hits.update({'page': 'unicorns'}, {'$inc': {'hits': 1}}, upsert=True)

db.hits.find_one()

# By default, update modifies just one document
db.unicorns.update({}, {'$set': {'vaccinated': True}});
for unicorn in db.unicorns.find({'vaccinated': True}):
    print unicorn

# multiple updates can be applied in a single operation, by setting named parameter multi=True
db.unicorns.update({}, {'$set': {'vaccinated': True}}, multi=True);
for unicorn in db.unicorns.find({'vaccinated': True}).limit(5):
    print unicorn

# ******** Chapter 3 - Mastering Find:
# *
# * https://github.com/karlseguin/the-little-mongodb-book/blob/master/en/mongodb.markdown#chapter-3---mastering-find
#

# We can ask mongodb to return just some fields when selecting documents
# _id is included by default unless we explicitly exclude it
# the rest of fields are not included by default
for doc in db.unicorns.find({}, {'_id': 0, 'name': 1}):
    print doc

# Sorting documents
for doc in db.unicorns.find({}, {'name': 1, 'weight': 1}).sort([('name', pymongo.ASCENDING), ('vampires', pymongo.DESCENDING)]):
    print doc

# Paging results
for doc in db.unicorns.find({}).sort([('name', pymongo.ASCENDING)]).skip(3).limit(2):
    print doc

# Counting results
db.unicorns.find({'vampires': {'$gt': 50}}).count()

# ******** Chapter 4 - Data Modelling:
# *
# * https://github.com/karlseguin/the-little-mongodb-book/blob/master/en/mongodb.markdown#chapter-4---data-modeling
#

# No joins are available in MongoDB.
# Let's going to create three employees: Leto, Duncan and Moneo. Leto is the manager.
from bson.objectid import ObjectId
db.employees.insert({'_id': ObjectId('4d85c7039ab0fd70a117d730'), 'name': 'Leto'})
db.employees.insert({'_id': ObjectId('4d85c7039ab0fd70a117d731'), 'name': 'Duncan',
                    'manager': ObjectId('4d85c7039ab0fd70a117d730')});
db.employees.insert({'_id': ObjectId('4d85c7039ab0fd70a117d732'), 'name': 'Moneo',
                    'manager': ObjectId('4d85c7039ab0fd70a117d730')});

for employee in db.employees.find({'manager': ObjectId('4d85c7039ab0fd70a117d730')}):
    print employee

# This relationships can be stored in arrays to model 1:N relationships
# Let's supose some employees can have many managers
db.employees.insert({'_id': ObjectId('4d85c7039ab0fd70a117d733'), 'name': 'Siona',
                    'manager': [ObjectId('4d85c7039ab0fd70a117d730'),
                                ObjectId('4d85c7039ab0fd70a117d732')]
                    })

# The previous query still works
for employee in db.employees.find({'manager': ObjectId('4d85c7039ab0fd70a117d730')}):
    print employee

# We can also model by nesting documents inside documents:
db.employees.insert({'_id': ObjectId('4d85c7039ab0fd70a117d734'), 'name': 'Ghanima',
                    'family': {'mother': 'Chani',
                               'father': 'Paul',
                               'brother': ObjectId('4d85c7039ab0fd70a117d730')}})

# Embedded documents can be queried with dot-notation:
for employee in db.employees.find({'family.mother': 'Chani'}):
    print employee

# DBRef objects allow to reference a collection and document from our document.
# Some drivers may get automatically the referenced object. Pymongo does so.

# Want to see the employee => manager example with DBRef? https://gist.github.com/javierarilos/d5fce5d50b1b9b8e2784

# ******** Chapter 5 - When to use MongoDB:
# *
# * https://github.com/karlseguin/the-little-mongodb-book/blob/master/en/mongodb.markdown#chapter-5---when-to-use-mongodb
#

# Out of the scope of this doc, see the link if you want to know more.

# Geospatial queries: http://mongly.openmymind.net/geo/index

# ******** Chapter 6 - Map and Reduce:
# *
# * https://github.com/karlseguin/the-little-mongodb-book/blob/master/en/mongodb.markdown#chapter-6---mapreduce
#

# Out of the scope of this doc, see the link if you want to know more.

# ******** Chapter 7 - Performance and Tools:
# *
# https://github.com/karlseguin/the-little-mongodb-book/blob/master/en/mongodb.markdown#chapter-7---performance-and-tools#
#

# Creating and deleting an index on name field
db.unicorns.ensure_index([('name', pymongo.DESCENDING)])
db.unicorns.drop_index([('name', pymongo.DESCENDING)])

# An index can be set as Unique (not repeated values for the indexed field)
db.unicorns.ensure_index([('name', pymongo.DESCENDING)], unique=True)

# Indexes can be set in embedded fiels and in array fields.
# Indexes can be compound on different fields:
db.unicorns.ensure_index([('name', pymongo.DESCENDING), ('vampires', pymongo.ASCENDING)])

# Explain, get some information on how query executes
db.unidorns.find().explain()
