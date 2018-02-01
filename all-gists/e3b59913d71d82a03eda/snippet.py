from cassandra.cluster import Cluster
from cassandra.policies import (TokenAwarePolicy, DCAwareRoundRobinPolicy, RetryPolicy)
from cassandra.query import (PreparedStatement, BoundStatement)

cluster = Cluster(
  contact_points=['127.0.0.1'],
   load_balancing_policy= TokenAwarePolicy(DCAwareRoundRobinPolicy(local_dc='datacenter1')),
   default_retry_policy = RetryPolicy()
  )
session = cluster.connect('demo')

# Insert one record into the users table
prepared_stmt = session.prepare ( "INSERT INTO users (lastname, age, city, email, firstname) VALUES (?, ?, ?, ?, ?)")
bound_stmt = prepared_stmt.bind(['Jones', 35, 'Austin', 'bob@example.com', 'Bob'])
stmt = session.execute(bound_stmt)

# Use select to get the user we just entered
prepared_stmt = session.prepare ( "SELECT * FROM users WHERE (lastname = ?)")
bound_stmt = prepared_stmt.bind(['Jones'])
stmt = session.execute(bound_stmt)
for x in stmt: print x.firstname, x.age

# Update the same user with a new age
prepared_stmt = session.prepare ("UPDATE users SET age = ? WHERE (lastname = ?)")
bound_stmt = prepared_stmt.bind([36,'Jones'])
stmt = session.execute(bound_stmt)

# Select and show the change
prepared_stmt = session.prepare ( "SELECT * FROM users WHERE (lastname = ?)")
bound_stmt = prepared_stmt.bind(['Jones'])
stmt = session.execute(bound_stmt)
for x in stmt: print x.firstname, x.age

# Delete the user from the users table
prepared_stmt = session.prepare ("DELETE FROM users WHERE (lastname = ?)")
bound_stmt = prepared_stmt.bind(['Jones'])
stmt = session.execute(bound_stmt)

# Show that the user is gone
results = session.execute("SELECT * FROM users")
for x in results: print x.firstname, x.age
