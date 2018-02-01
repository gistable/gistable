# dropping a database via pymongo
from pymongo import Connection
c = Connection()
c.drop_database('mydatabase')

# drop a collection via pymongo
from pymongo import Connection
c = Connection()
c['mydatabase'].drop_collection('mycollection')
