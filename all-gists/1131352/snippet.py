#!/usr/bin/python

# Raja Selvaraj <rajajs at gmail>

"""
Demonstrate use of pymongo to connect to a mongodb database on a hosted server,
specifically mongolab
"""

# Use a database already created on mongolab 
server = 'xxxxx.mongolab.com'
port = xxxxx
db_name = 'xxxx'
username = 'xxxxx'
password = 'xxxxxx'


from pymongo import Connection

# what versions are we using
import sys
print 'Python version', sys.version

import pymongo
print 'Pymongo version', pymongo.version
##

# connect to server
print '\nConnecting ...'
conn = Connection(server, port)

# Get the database
print '\nGetting database ...'
db = conn[db_name]

# Have to authenticate to get access
print '\nAuthenticating ...'
db.authenticate(username, password)

# Get the documents
posts = db.posts
print '\nNumber of posts', posts.find().count()

# Remove all old posts
posts.remove()
print '\nNumber of posts after removal', posts.find().count()

# Let us add one post
post = {'Name' : 'Human',
        'Heart rate' : 60,
        'Longevity' : 70,
        'tags' : ['domestic', 'omnivore']}
posts.insert(post)
print '\nNumber of posts after first insert', posts.find().count()

# Bulk inserts
new_posts = [{'Name': 'Cat',
              'Heart rate' : 150,
              'Longevity' : 15,
              'tags' : ['domestic', 'carnivore']},
             {'Name' : 'Small dog',
              'Heart rate' : 100,
              'Longevity' : 10,
              'tags' : ['domestic', 'omnivore']},
             {'Name' : 'Medium Dog',
              'Heart rate' : 90,
              'Longevity' : 15,
              'tags' : ['domestic', 'omnivore']},
             {'Name' : 'Large dog',
              'Heart rate' : 75,
              'Longevity' : 17,
              'tags' : ['domestic', 'omnivore']},
             {'Name' : 'Chicken',
              'Heart rate' : 275,
              'Longevity' : 15,
              'tags' : ['domestic', 'omnivore']},
             {'Name' : 'Elephant',
              'Heart rate' : 30,
              'Longevity' : 70,
              'tags' : ['wild', 'herbivore']},
             {'Name' : 'Giraffe',
              'Heart rate' : 65,
              'Longevity' : 20,
              'tags' : ['wild', 'herbivore']}]
posts.insert(new_posts)
print '\nNumber of posts after bulk insert', posts.find().count()

##  Querying
# Let us see all the posts
print '\nAll posts'
for post in posts.find():
    print post

# find_one
print '\nOne post only'    
print posts.find_one()

# Find animals with heart rate > 100
print '\nAnimals with heart rate more than 100'
for post in posts.find({'Heart rate' : {"$gt" : 100}}):
    print post
    
# Find animals with longevity between 20 and 70 (inclusive)
print '\nAnimals with longevity between 20 and 70 (inclusive range)'
for post in posts.find({'Longevity' : {"$gte" : 20, "$lte" : 100}}):
    print post

# create an index to speed up queries
# using ensure_index instead would create an index only if it does not exist
print '\nCreating index for heart rate'
posts.create_index("Heart rate")
    
# Find by name - string matching
print '\nRetrieve entry for elephant'
print posts.find_one({'Name' : 'Elephant'})

# Regex matching to find substring
print '\nRetrieve entries for all dogs'
for post in posts.find({'Name' : {'$regex' : 'dog'}}):
    print post

# Do same with more regex options
print '\nRetrieve entries for all dogs by using case insensitive matching'
import re
regex = re.compile('dog', re.IGNORECASE)
for post in posts.find({'Name' : regex}):
    print post

# Query for tags
print '\nRetrieve entries for all domestic omnivores'
for post in posts.find({'tags' : {'$all' : ['domestic', 'omnivore']}}):
    print post
    
# close the connection
print '\nClosing the connection'
conn.disconnect()


## References
##

# 1. http://api.mongodb.org/python/current/tutorial.html
# 2. http://www.mongodb.org/display/DOCS/Advanced+Queries
# 2. http://stackoverflow.com/questions/3483318/performing-regex-queries-with-pymongo
# 3. Data for posts - http://www.sjsu.edu/faculty/watkins/longevity.htm
