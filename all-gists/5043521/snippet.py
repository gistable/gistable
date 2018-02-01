# Torndb is a very thin wrapper around MySQLdb that makes it even easier to use MySQL.
# Because it is very light, one can just go through the one-file python source
# to learn how to use it.

# Installation: pip install torndb
# Official doc: http://torndb.readthedocs.org/en/latest/
# Source: https://github.com/bdarnell/torndb/blob/master/torndb.py

from torndb import Connection

# Connect by IP address
db = Connection('127.0.0.1', 'database_name', user='root', password='root')
# Connect by IP address with port
db = Connection('127.0.0.1:1234', 'database_name', user='root', password='root')
# Connect by socket
db = Connection('/tmp/mysql.sock', 'database_name', user='root', password='root')
# Connection over SSH, open a SSH tunnel with
#     ssh -L 1234:localhost:3306 user@server.com
# then connect to 127.0.0.1:1234

# Retreive one object
post = db.get("SELECT * FROM posts LIMIT 1")

# Retreive several objects
for post in db.query("SELECT * FROM posts"):
    print post.title
  
# Insert one entry
db.execute("INSERT INTO posts (user_id, content) VALUES (%s, %s)", 12, "hello world !")

# Insert multiple entries
values = [(12, "hello"), (17, "world"), (22, "blah")]
db.executemany("INSERT INTO posts (user_id, content) VALUES (%s, %s)", values)