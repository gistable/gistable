import select
import datetime

import psycopg2
import psycopg2.extensions

from sqlalchemy import create_engine, text

engine = create_engine("postgresql+psycopg2://vagrant@/postgres")

#conn = psycopg2.connect(database="postgres", user="vagrant")
#conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

#curs = conn.cursor()
#curs.execute("LISTEN test1;")
#curs.execute("LISTEN test2;")
conn = engine.connect()
conn.execute(text("LISTEN test1; LISTEN test2").execution_options(autocommit=True))
print "Waiting for notifications on channels 'test1', 'test2' with SQL Alchemy"
while 1:
    #conn.commit()
    if select.select([conn.connection],[],[],5) == ([],[],[]):
        print "Timeout"
    else:
        conn.connection.poll()
        while conn.connection.notifies:
            notify = conn.connection.notifies.pop()
            print "Got NOTIFY:", datetime.datetime.now(), notify.pid, notify.channel, notify.payload
