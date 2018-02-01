import sqlite3

# open connection and get a cursor
conn = sqlite3.connect(':memory:')
c = conn.cursor()

# create schema for a new table
c.execute('CREATE TABLE IF NOT EXISTS sometable (name, age INTEGER)')
conn.commit()

# insert a new row
c.execute('INSERT INTO sometable values (?, ?) ', ('John Doe', 37))
conn.commit()

# extend schema during runtime
c.execute('ALTER TABLE sometable ADD COLUMN gender TEXT')
conn.commit()

# add another row
c.execute('INSERT INTO sometable values (?, ?, ?) ', ('Jane Doe', 34, 'female'))
conn.commit()

# get a single row
c.execute('SELECT name, age FROM sometable WHERE name = ?', ('John Doe', ))
row = list(c)[0]
john = dict(name=row[0], age=row[1])

