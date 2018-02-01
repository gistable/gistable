import pymongo
from pymongo import Connection
from pymongo.dbref import DBRef
from pymongo.database import Database

# connect
connection = Connection()
db = Database(connection, "things")

# clean up
db.owners.remove()
db.tasks.remove()

# owners and tasks
db.owners.insert({"name":"Jim"})
db.tasks.insert([
    {"name": "read"},
    {"name": "sleep"}
    ])

# update jim with tasks: reading and sleeping
reading_task = db.tasks.find_one({"name": "read"})
sleeping_task = db.tasks.find_one({"name": "sleep"})

jim_update = db.owners.find_one({"name": "Jim"})
jim_update["tasks"] = [
    DBRef(collection = "tasks", id = reading_task["_id"]),
    DBRef(collection = "tasks", id = sleeping_task["_id"])
    ]

db.owners.save(jim_update)

# get jim fresh again and display his tasks
fresh_jim = db.owners.find_one({"name":"Jim"})
print "Jim's tasks are:"
for task in fresh_jim["tasks"]:
    print db.dereference(task)["name"]
