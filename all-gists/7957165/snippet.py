# -*- coding:utf-8 -*-
import json
import sqlite3

JSON_FILE = "some.json"
DB_FILE = "some.db"

traffic = json.load(open(JSON_FILE))
conn = sqlite3.connect(DB_FILE)

foo = traffic[0]["foo"]
bar = traffic[0]["bar"]

data = [foo, bar]

c = conn.cursor()
c.execute('create table table_name (foo, bar)')
c.execute('insert into table_name values (?,?)', data)

conn.commit()
c.close()
