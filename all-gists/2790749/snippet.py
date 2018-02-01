##########################################################
# django postgres polling - LISTEN

import psycopg2.extensions
import select

from django.db import connection

crs = connection.cursor()  # get the cursor and establish the connection.connection
pg_con = connection.connection
pg_con.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
crs.execute('LISTEN test;');

print "Waiting for notifications on channel 'test'"
while 1:
    if select.select([pg_con],[],[],5) == ([],[],[]):
        print "Timeout"
    else:
        pg_con.poll()
        while pg_con.notifies:
            notify = pg_con.notifies.pop()
            print "Got NOTIFY:", `notify`


            
##########################################################
# django postgres polling - NOTIFY

from django.db import connection
import psycopg2.extensions

crs = connection.cursor()  # get the cursor and establish the connection.connection
connection.connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
crs.execute('NOTIFY test;');

crs.execute('SELECT pg_sleep(6); NOTIFY test;');